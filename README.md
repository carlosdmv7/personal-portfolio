# Carlos De Manuel — Analytics Engineer

Personal portfolio. Static HTML/CSS/JS, no build step, served from GitHub Pages
at **<https://carlosdmv7.github.io/personal-portfolio/>**.

## Structure

```
index.html                                  home
projects/job-market-intelligence/           case study (own URL, title, og:image)
projects/spanish-housing-radar/             case study
styles.css                                  design system — all colour lives in :root
site.js                                     nav, accordion, reveal-on-scroll
freshness.js                                the freshness strip's live upgrade
data/freshness.json                          static fallback + schema reference
cv/carlos-de-manuel-analytics-engineer.pdf   linked from the hero and Contact
docs/freshness-contract.md                   status.json schema + CI snippet
tools/contrast-check.py                      WCAG checker for the palette
tools/make-og-images.py                      regenerates the 1200x630 og cards
tools/make-icons.py                          regenerates favicon/apple-touch PNGs
```

## Ground rules

**Every figure on this site is read from an artefact, never typed from memory.**
dbt model and test counts come from each project's `target/manifest.json`; the
IND sponsor count is the row count of that project's seed CSV. If a number
changes, re-read the manifest — don't estimate.

Current values (verified 25 Jul 2026):

| | Job Market Intelligence | Spanish Housing Radar |
|---|---|---|
| dbt models | 9 (+1 seed) | 13 (+2 seeds) |
| dbt data tests | 45 | 90 |
| sources | 5 job-board APIs | 3 (Idealista, Fotocasa, INE) |
| other | 12,797 IND recognised sponsors | 4 Streamlit pages |

**Colour.** All 22 tokens live in `:root` in `styles.css`; there are no hex or
`rgba()` literals anywhere else in the file. `--petrol-900` is the only dark
surface (header band, footer band, freshness strip), always with `--sand-100`
text. `--amber-500` and `--sand-100` are never text on a light background.
`--rust-500` is graphical only; rust *text* and rust *fills with white labels*
use `--rust-700`.

Before shipping a colour change:

```bash
python3 tools/contrast-check.py      # exits non-zero on any violation
```

It covers all 36 pairs the stylesheet produces, and asserts that the forbidden
pairs (`--teal-500` on `--petrol-900`, amber/sand as text on light) are not
used as text. Add a row when you add a pair.

**The freshness strip** shows real pipeline state per project and must never
show a spinner or an error. Its fallback ships in the HTML already populated;
`freshness.js` only upgrades values on a successful fetch. See
[docs/freshness-contract.md](docs/freshness-contract.md) — the `status.json`
publishing step still needs adding to the two project repos, so the strip
currently shows the static snapshot.

## Regenerating assets

Both scripts need `pillow`, and the og cards need three fonts fetched once:

```bash
python3 -m venv .venv && .venv/bin/pip install pillow
mkdir -p fonts && cd fonts
curl -sSLO "https://github.com/google/fonts/raw/main/ofl/archivo/Archivo%5Bwdth,wght%5D.ttf"
curl -sSLO "https://github.com/google/fonts/raw/main/ofl/publicsans/PublicSans%5Bwght%5D.ttf"
curl -sSLO "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Medium.ttf"
cd ..
.venv/bin/python tools/make-og-images.py --out images
.venv/bin/python tools/make-icons.py --out images
```

`fonts/` and `.venv/` are gitignored — the site loads its webfonts from Google
Fonts with `display=swap`.

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. A plain `file://` open also works, except
the freshness strip's fetch is cross-origin from `file://` and falls back to
the static snapshot — which is the intended behaviour, just not the live one.
