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
lychee.toml                                  link-checker config (what's excluded, and why)
.github/workflows/link-check.yml             fails the build on any 4xx link
images/jmi/                                  app screenshots for the JMI case study
tools/contrast-check.py                      WCAG checker for the palette
tools/make-og-images.py                      regenerates the 1200x630 og cards
tools/make-icons.py                          regenerates favicon/apple-touch PNGs
tools/make-shots.py                          downscales the JMI app screenshots
```

## Ground rules

**Every figure on this site is read from an artefact, never typed from memory.**
dbt model and test counts come from each project's `target/manifest.json`; the
IND sponsor count is the row count of that project's seed CSV. If a number
changes, re-read the manifest — don't estimate.

Current values (verified 19 Sep 2026; Spanish Housing Radar re-verified 25 Sep 2026):

| | Job Market Intelligence | Spanish Housing Radar |
|---|---|---|
| dbt models | 9 (+1 seed) | 17 (+3 seeds) |
| dbt data tests | 53 | 153 |
| sources | 5 job-board APIs | 3 (Idealista, INE price index, INE income) |
| app pages | 7 Streamlit pages | 6 Streamlit pages |
| other | 12,797 IND recognised sponsors | — |

The Job Market Intelligence case study also quotes warehouse figures — open
roles per market, how much of the corpus the LLM has read — which move with
every daily run. Those carry the date they were measured, in the copy and in
the screenshot captions, rather than being presented as standing facts. Keep
the copy and the screenshots on the *same* run: the app prints its own counts
in every header, so a reader compares them without being asked to.

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
`freshness.js` only upgrades values on a successful fetch, reading each
project's `docs/status.json` from `raw.githubusercontent.com`. See
[docs/freshness-contract.md](docs/freshness-contract.md) — Job Market
Intelligence publishes its feed from the warehouse into its GitHub Pages
artifact, beside its dbt docs, so no commit ever lands on `main` for it.
Spanish Housing Radar has no feed yet and keeps showing the snapshot, which is
the designed fallback rather than a bug.

**Links.** A dead link is the most expensive failure this site can have: a
recruiter clicks "Live app", gets a 404, and there is no second click.
`.github/workflows/link-check.yml` runs [lychee](https://lychee.cli.rs) over
every HTML page and markdown file on push, on PRs, and weekly — the weekly run
is the one that matters, since a repo someone renames doesn't push a commit
here. Any 4xx fails the build.

```bash
lychee --config lychee.toml './**/*.html' './README.md' './docs/**/*.md'
```

Two things are excluded on purpose, both documented in `lychee.toml`: LinkedIn
(answers every bot with HTTP 999 whether or not the profile exists, so the
check can only ever be a false negative — verify that one by hand) and the
`status.json` feeds (a 404 there is the freshness strip's designed fallback).

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

The Job Market Intelligence screenshots are mirrored from that project's repo,
where they are captured against the live warehouse. They ship at 1440px in WebP
(~375 KB for the set, against 1.7 MB for the source PNGs) and every one is
lazy-loaded except the hero:

```bash
.venv/bin/python tools/make-shots.py --src ~/projects/job-market-intelligence/docs/img
```

Six of the repo's seven screens are used; `--only` overrides the selection.
Find Jobs is the one left out — My Fit already shows a ranked table of the same
postings. The selection is not cosmetic: when ADR 0011 folded the standalone
Netherlands visa page into Market Detail, `visa-sponsorship.png` stopped
existing and the case study had to move with it. If a screen disappears
upstream, this list is where it shows up.

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. A plain `file://` open also works; the
freshness strip may or may not reach its feeds from a `file://` origin
depending on the browser, and falls back to the static snapshot when it can't —
which is the intended behaviour, just not the live one.
