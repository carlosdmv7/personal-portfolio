# Working in this repo

Static HTML/CSS/JS, no build step, deployed from the repo root by GitHub Pages.
There is nothing to compile: edit the file, push, it is live.

Read [README.md](README.md) first — the ground rules live there, not here.
This file only covers what an agent gets wrong that a human reading the README
would not.

## The one rule that matters

**Every figure on this site is a claim about a real system, and a reader can
check it.** Re-read it from the artefact — `target/manifest.json`, a seed's row
count, a warehouse query — and never carry one over from memory or from an
earlier draft in the same session. A number that was right last month is the
most convincing way to be wrong.

The same applies to the job title in the experience section. It is verifiable in
a reference call. Do not smooth it into something that sells better.

## Claims that would be false

The Job Market Intelligence case study is close enough to several true things
that the false version reads fine. It is a *portfolio*, so being caught once
costs more than the claim ever earned:

| Do not write | Because |
|---|---|
| "Orchestrated with Prefect" | The flows are Prefect-*instrumented*; the scheduler is a GitHub Actions cron. |
| Docker, Kubernetes, containers | None are used. |
| Any classifier accuracy figure | There is no labelled evaluation set. "Labelling in progress" is not a way around this. |
| "Netherlands-focused" | Spain is the largest market in the corpus. |
| "Complete market coverage" | It is partial. State the share; do not round it up or drop it. |
| "Secure" or "hardened" text-to-SQL | It is guard-railed, which is a weaker and honest word. |

Partial coverage is a feature of the write-up, not an embarrassment to manage.

## Before saying it is done

No browser is available here, so these are the checks that stand in for looking
at the page:

```bash
python3 tools/contrast-check.py                  # must exit 0
lychee --config lychee.toml './**/*.html' './README.md' './docs/**/*.md'
```

Also parse every touched HTML file for tag balance — an unclosed `<div>` in a
case study does not fail any of the above, and silently collapses the layout.
That one has bitten twice.

After pushing, `gh run list` and a `curl | grep` against the live URL, because
"the commit landed" is not the same claim as "the page says what I meant".

## Conventions

Conventional Commits. Branch and open a PR rather than pushing to `main`; the
link check runs on PRs, which is the point of having it.

Copy is British English, plain, and short. Match the voice already on the page:
concrete nouns, no "leveraged", no "passionate", no em-dash-joined superlatives.
If an existing entry is three bullets, write three bullets.
