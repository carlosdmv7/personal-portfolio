# Freshness strip — data contract

The portfolio renders a thin band showing live pipeline state per project:

```
last ingest · rows in warehouse · dbt tests passing · last CI run
```

The positioning claim on this site is "data you can trust". A portfolio that
proves its own claims live is the argument, so the strip reads real state from
each project rather than restating a number typed into HTML.

## How it works

1. Each project's CI writes a `status.json` and publishes it to that project's
   GitHub Pages branch.
2. The portfolio fetches those URLs client-side ([freshness.js](../freshness.js)).
   Both projects are served from `carlosdmv7.github.io`, the same origin as the
   portfolio, so there is no CORS involved.
3. **The page never shows a spinner and never shows an error.** The strip ships
   in the HTML with a verified static fallback already rendered. JS only
   replaces values on success. A failed fetch, a 404, a timeout, malformed JSON
   or JS being disabled entirely all leave the static snapshot visible, and the
   label under the heading says which state you are looking at.

Static fallback values live in [`data/freshness.json`](../data/freshness.json).
`rows` and `last_ingest` are deliberately `null` there — they are runtime facts
only the live feed can supply, and hardcoding a plausible number would defeat
the purpose of the strip. They render as an em dash until the feed is live.

## Schema

`status.json`, published at the Pages root of each project:

```json
{
  "schema": 1,
  "project": "job-market-intelligence",
  "generated_at": "2026-07-25T05:14:03Z",
  "last_ingest": "2026-07-25T05:12:41Z",
  "rows": 18432,
  "dbt_tests": { "passed": 45, "total": 45 },
  "last_ci": {
    "status": "success",
    "at": "2026-07-25T05:14:03Z",
    "url": "https://github.com/carlosdmv7/job-market-intelligence/actions/runs/123456789"
  }
}
```

| Field | Type | Meaning |
|---|---|---|
| `schema` | int | Contract version. Currently `1`. |
| `project` | string | Repo slug. Must match the strip's `data-freshness-project`. |
| `generated_at` | ISO 8601 UTC | When this file was written. |
| `last_ingest` | ISO 8601 UTC | Completion of the most recent successful extract. |
| `rows` | int | Row count of the primary fact table in the warehouse. |
| `dbt_tests.passed` / `.total` | int | From `dbt build`'s run results. |
| `last_ci.status` | `success` \| anything else | Anything other than `success` renders as a failure. |
| `last_ci.at` | ISO 8601 UTC | When the run finished. |
| `last_ci.url` | https URL | Optional. Links the cell to the run. |

Every field is optional in practice: the strip upgrades the cells it can parse
and leaves the rest on their fallback value. A partial or half-broken feed
degrades one cell, not the band.

### State derivation

The dot beside each project name is the **worst** of the available signals, so
it can't look healthy while something underneath is broken:

| State | Condition | Colour |
|---|---|---|
| fresh | `last_ingest` within 48h, tests all passing, CI green | `--teal-200` |
| stale | `last_ingest` between 48h and 14 days | `--amber-500` |
| cold | `last_ingest` older than 14 days | `--amber-500`, "cold" label |
| failing | any dbt test failing, or `last_ci.status != "success"` | `--rust-300` |

State is never conveyed by colour alone — each cell carries its own text.

## Publishing it from a project's CI

Not yet wired up in the project repos. Paste this step at the end of the
pipeline workflow, after `dbt build`:

```yaml
      - name: Publish status.json
        if: always()
        run: |
          mkdir -p _pages
          python - <<'PY'
          import json, os, pathlib, datetime

          # dbt writes run_results.json for every invocation
          rr = json.load(open("dbt/jmi/target/run_results.json"))
          tests = [r for r in rr["results"] if r["unique_id"].startswith("test.")]
          passed = sum(1 for r in tests if r["status"] == "pass")

          # row count of the primary fact table
          import duckdb
          con = duckdb.connect(f"md:{os.environ['MOTHERDUCK_DB']}?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}")
          rows = con.sql("select count(*) from marts.FT_JOB_POSTING").fetchone()[0]

          now = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
          pathlib.Path("_pages/status.json").write_text(json.dumps({
              "schema": 1,
              "project": os.environ["GITHUB_REPOSITORY"].split("/")[-1],
              "generated_at": now,
              "last_ingest": os.environ.get("INGEST_COMPLETED_AT") or now,
              "rows": rows,
              "dbt_tests": {"passed": passed, "total": len(tests)},
              "last_ci": {
                  "status": os.environ["JOB_STATUS"],
                  "at": now,
                  "url": f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
              },
          }, indent=2) + "\n")
          PY
        env:
          JOB_STATUS: ${{ job.status }}
          MOTHERDUCK_TOKEN: ${{ secrets.MOTHERDUCK_TOKEN }}
          MOTHERDUCK_DB: ${{ vars.MOTHERDUCK_DB }}

      - name: Deploy to Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: _pages
          keep_files: true          # don't wipe the dbt docs already published there
```

`keep_files: true` matters for `spanish-housing-radar`, whose Pages branch
already serves the dbt docs site — `status.json` needs to land beside it, not
replace it.

Adjust the manifest path (`dbt/jmi/target` vs `transform/target`) and the fact
table per project.

## Rendering it inside the Streamlit apps

The strip is meant to look the same on this site and inside both apps. The
band is a petrol bar with `--sand-100` mono text; in Streamlit the equivalent
is a single `st.markdown(..., unsafe_allow_html=True)` block reading the same
`status.json` the app already has warehouse access to compute directly. Not
implemented here — this repo's scope is the portfolio side.
