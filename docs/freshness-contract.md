# Freshness strip — data contract

The portfolio renders a thin band showing live pipeline state per project:

```
last ingest · rows in warehouse · dbt tests passing · last CI run
```

The positioning claim on this site is "data you can trust". A portfolio that
proves its own claims live is the argument, so the strip reads real state from
each project rather than restating a number typed into HTML.

## How it works

1. Each project's CI writes a `status.json` and commits it to `docs/status.json`
   on that project's default branch.
2. The portfolio fetches it client-side ([freshness.js](../freshness.js)) from
   `raw.githubusercontent.com`:

   ```
   https://carlosdmv7.github.io/job-market-intelligence/status.json
   https://raw.githubusercontent.com/carlosdmv7/spanish-housing-radar/main/docs/status.json
   ```

   That host serves `Access-Control-Allow-Origin: *`, so the cross-origin fetch
   works from GitHub Pages without any proxy. Reading the branch directly also
   means the strip does not depend on either project having Pages enabled.
3. **The page never shows a spinner and never shows an error.** The strip ships
   in the HTML with a verified static fallback already rendered. JS only
   replaces values on success. A failed fetch, a 404, a timeout, malformed JSON
   or JS being disabled entirely all leave the static snapshot visible, and the
   label under the heading says which state you are looking at.

### Where the feed comes from

Job Market Intelligence publishes it. Its pipeline already appends every run to
`meta.pipeline_run` **in the warehouse** — the committed-file version was tried
and abandoned, because writing `status.json` to `main` meant two bot commits a
day and 58 in the first month, burying the human history.

So the file is generated instead of committed. `jmi_flows.status_json` reads the
newest run and writes `status.json` into the GitHub Pages artifact that already
carries that project's dbt docs, which is why the URL is the Pages origin and
not `raw.githubusercontent.com`. It runs daily at 06:30 UTC, after the 05:15
pipeline, and the step is `continue-on-error`: a missing token or an unreachable
warehouse leaves the file absent rather than failing the docs deploy.

Spanish Housing Radar does not publish one yet, so its row keeps showing the
verified snapshot — which is the designed fallback, and the reason the fallback
ships populated in the HTML rather than being fetched.

Static fallback values live in [`data/freshness.json`](../data/freshness.json).
`rows_in_warehouse` and `last_ingest_at` are deliberately `null` there — they
are runtime facts only the live feed can supply, and hardcoding a plausible
number would defeat the purpose of the strip. They render as an em dash until
the feed is live.

## Schema

`status.json`, committed to `docs/status.json` in each project:

```json
{
  "project": "job-market-intelligence",
  "generated_at": "2026-09-16T05:14:03Z",
  "last_ingest_at": "2026-09-16T05:12:41Z",
  "rows_in_warehouse": 65964,
  "dbt_tests_passed": 53,
  "dbt_tests_total": 53,
  "last_run_conclusion": "success"
}
```

| Field | Type | Meaning |
|---|---|---|
| `project` | string | Repo slug. Must match the strip's `data-freshness-project`, or the whole feed is ignored. |
| `generated_at` | ISO 8601 UTC | When this file was written — i.e. when the CI run finished. Renders as the "last CI run" time. |
| `last_ingest_at` | ISO 8601 UTC | Completion of the most recent successful extract. Rendered relative ("6h ago"), with the absolute UTC timestamp on hover. |
| `rows_in_warehouse` | int | Row count of the primary fact table. |
| `dbt_tests_passed` / `dbt_tests_total` | int | From `dbt build`'s run results. |
| `last_run_conclusion` | `success` \| anything else | The GitHub Actions conclusion. Anything other than `success` renders as a failure. |

Apart from `project`, every field is optional in practice: the strip upgrades
the cells it can parse and leaves the rest on their fallback value. A partial
or half-broken feed degrades one cell, not the band.

### State derivation

The dot beside each project name is the **worst** of the available signals, so
it can't look healthy while something underneath is broken:

| State | Condition | Colour |
|---|---|---|
| fresh | `last_ingest_at` within 48h, tests all passing, CI green | `--teal-200` |
| stale | `last_ingest_at` between 48h and 14 days | `--amber-500` |
| cold | `last_ingest_at` older than 14 days | `--amber-500`, "cold" label |
| failing | any dbt test failing, or `last_run_conclusion != "success"` | `--rust-300` |

State is never conveyed by colour alone — each cell carries its own text.

## Publishing it from a project's CI

Not yet wired up in the project repos — until it is, the strip shows the
verified static snapshot, which is the designed behaviour and not a bug. Paste
this at the end of the pipeline workflow, after `dbt build`. The job needs
`permissions: contents: write` to push the commit.

```yaml
      - name: Write docs/status.json
        if: always()
        run: |
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
          out = pathlib.Path("docs/status.json")
          out.parent.mkdir(parents=True, exist_ok=True)
          out.write_text(json.dumps({
              "project": os.environ["GITHUB_REPOSITORY"].split("/")[-1],
              "generated_at": now,
              "last_ingest_at": os.environ.get("INGEST_COMPLETED_AT") or now,
              "rows_in_warehouse": rows,
              "dbt_tests_passed": passed,
              "dbt_tests_total": len(tests),
              "last_run_conclusion": os.environ["JOB_STATUS"],
          }, indent=2) + "\n")
          PY
        env:
          JOB_STATUS: ${{ job.status }}
          MOTHERDUCK_TOKEN: ${{ secrets.MOTHERDUCK_TOKEN }}
          MOTHERDUCK_DB: ${{ vars.MOTHERDUCK_DB }}

      - name: Commit docs/status.json
        if: always()
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add docs/status.json
          # Nothing to do when the run produced identical numbers.
          git diff --quiet --cached || git commit -m "chore: refresh docs/status.json [skip ci]"
          git push
```

Adjust the run-results path (`dbt/jmi/target` vs `transform/target`) and the
fact table per project.

## Rendering it inside the Streamlit apps

The strip is meant to look the same on this site and inside both apps. The
band is a petrol bar with `--sand-100` mono text; in Streamlit the equivalent
is a single `st.markdown(..., unsafe_allow_html=True)` block reading the same
`status.json` the app already has warehouse access to compute directly. Not
implemented here — this repo's scope is the portfolio side.
