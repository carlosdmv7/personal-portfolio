/* ============================================================
   Freshness strip — live pipeline state per project.

   Contract: each project's CI publishes a small status.json to its GitHub
   Pages branch. See docs/freshness-contract.md for the schema and a
   paste-ready workflow step.

   Design rule: the page must NEVER show a spinner or an error. The strip is
   rendered server-side (well, statically) in the HTML with a verified
   fallback already in place. This script only *upgrades* those values if a
   live fetch succeeds. If the fetch fails, is slow, is malformed, or JS never
   runs at all, the visitor sees the static snapshot and a label that says so.
   ============================================================ */
(() => {
    'use strict';

    const TIMEOUT_MS = 4000;
    const FRESH_MS = 48 * 3600 * 1000;        // <= 48h  -> fresh
    const STALE_MS = 14 * 24 * 3600 * 1000;   // <= 14d  -> stale, older -> cold

    const nf = new Intl.NumberFormat('en-GB');

    /** "4h ago" / "3d ago" / "5mo ago" — null if unparseable. */
    function ago(iso) {
        const t = Date.parse(iso);
        if (Number.isNaN(t)) return null;
        const s = Math.max(0, (Date.now() - t) / 1000);
        if (s < 90) return 'just now';
        if (s < 5400) return `${Math.round(s / 60)}m ago`;
        if (s < 172800) return `${Math.round(s / 3600)}h ago`;
        if (s < 5184000) return `${Math.round(s / 86400)}d ago`;
        return `${Math.round(s / 2592000)}mo ago`;
    }

    function absolute(iso) {
        const t = Date.parse(iso);
        if (Number.isNaN(t)) return '';
        return new Date(t).toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
    }

    function setCell(row, key, text, title) {
        const el = row.querySelector(`[data-fresh="${key}"]`);
        if (!el || text == null) return false;
        el.textContent = text;
        if (title) el.title = title;
        return true;
    }

    /** Worst-of the per-signal states, so the dot reflects the real situation. */
    function rank(state) {
        return { fresh: 0, stale: 1, cold: 2, failing: 3 }[state] ?? 0;
    }

    function ageState(iso) {
        const t = Date.parse(iso);
        if (Number.isNaN(t)) return null;
        const d = Date.now() - t;
        if (d <= FRESH_MS) return 'fresh';
        if (d <= STALE_MS) return 'stale';
        return 'cold';
    }

    async function load(url) {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
        try {
            const res = await fetch(url, { signal: ctrl.signal, cache: 'no-store' });
            if (!res.ok) return null;
            const data = await res.json();
            const usable = data && typeof data === 'object' && !Array.isArray(data);
            return usable ? data : null;
        } catch {
            return null;              // offline, 404, CORS, timeout, bad JSON — all the same
        } finally {
            clearTimeout(timer);
        }
    }

    /* Upgrade whatever parsed and report whether the feed was actually usable.
       A 200 response with the wrong shape must NOT be reported as live, and
       must not light a healthy dot — that would be the strip lying about
       itself, which is the one thing it exists not to do. */
    function apply(row, d) {
        let worst = null;
        let updated = 0;
        const bump = (s) => { if (s && (worst === null || rank(s) > rank(worst))) worst = s; };

        if (typeof d.last_ingest === 'string') {
            const rel = ago(d.last_ingest);
            if (rel && setCell(row, 'last_ingest', rel, absolute(d.last_ingest))) {
                updated++;
                bump(ageState(d.last_ingest));
            }
        }

        if (Number.isFinite(d.rows) && setCell(row, 'rows', nf.format(d.rows))) {
            updated++;
        }

        const t = d.dbt_tests;
        if (t && Number.isFinite(t.passed) && Number.isFinite(t.total)) {
            if (setCell(row, 'dbt_tests', `${nf.format(t.passed)} / ${nf.format(t.total)}`)) updated++;
            if (t.passed < t.total) bump('failing');
        }

        const ci = d.last_ci;
        if (ci && typeof ci.at === 'string') {
            const rel = ago(ci.at);
            const ok = ci.status === 'success';
            if (rel && setCell(row, 'last_ci', `${ok ? 'passed' : (ci.status || 'failed')} · ${rel}`, absolute(ci.at))) {
                updated++;
            }
            if (!ok) bump('failing');
            const link = row.querySelector('[data-fresh-ci-link]');
            if (link && typeof ci.url === 'string' && /^https:\/\//.test(ci.url)) {
                link.href = ci.url;
                link.hidden = false;
            }
        }

        if (!updated) return false;              // nothing usable — stay on the fallback
        if (worst !== null) row.dataset.state = worst;   // otherwise leave the grey dot
        row.dataset.freshnessSource = 'live';
        return true;
    }

    function init() {
        const rows = [...document.querySelectorAll('[data-freshness-url]')];
        if (!rows.length) return;

        Promise.all(rows.map(async (row) => {
            const d = await load(row.dataset.freshnessUrl);
            return d ? apply(row, d) : false;
        })).then((results) => {
            const live = results.filter(Boolean).length;
            const label = document.querySelector('[data-freshness-source]');
            if (!label) return;
            if (live === results.length) {
                label.textContent = 'Live — fetched from each project’s CI just now.';
            } else if (live > 0) {
                label.textContent = `Live for ${live} of ${results.length} projects; the rest show the last verified snapshot.`;
            }
            // live === 0: leave the static wording that shipped in the HTML.
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
