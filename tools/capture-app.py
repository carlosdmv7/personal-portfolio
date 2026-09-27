#!/usr/bin/env python3
"""Capture tall screenshots of the live Streamlit apps for tools/make-shots.py.

Every page is captured at 2x and well past the point the case study cuts it;
make-shots.py then crops each one at an empty band of page background, never
through a chart or a table. Each app is loaded from `/~/+/`, the page Streamlit
Cloud frames, with `?embed=true`: no Cloud chrome, and the widgets are in the
top-level document, where the script can type into them.

Every page is captured 1440px wide, including the ones shown beside the prose
at ~590px. A narrower viewport would make the app's type larger there, but its
tables stop fitting: at 1000px the Deals table loses the column its caption is
about. The side figures link to the full image instead.

    .venv/bin/python tools/capture-app.py --out /tmp/shots

A Cloud app that has gone to sleep serves a "Zzzz" page instead: open it in a
browser, wake it, and run this again once it has loaded.

Requires: playwright (and `playwright install chromium`).
"""
from __future__ import annotations

import argparse
import pathlib
import time

from playwright.sync_api import sync_playwright

JMI = "https://job-market-intelligence-carlosdmv7.streamlit.app/~/+"
SHR = "https://spanish-housing-radar-carlosdmv7.streamlit.app/~/+"
PAGES = {
    "jmi-home": f"{JMI}/",
    "jmi-my-fit": f"{JMI}/CV_Match",
    "jmi-market-detail": f"{JMI}/Market_Detail?market=NL",
    "shr-home": f"{SHR}/",
    "shr-opportunities": f"{SHR}/deals",
}
# My Fit shows nothing until it has a CV: a short one that names a typical
# analytics-engineering stack, pasted the way a visitor would.
SAMPLE_CV = (
    "Data & Analytics Engineer. Python, SQL, dbt, Airflow, Prefect, Docker, Git, CI/CD. "
    "Snowflake, DuckDB, AWS. Pandas, machine learning, Power BI, Streamlit."
)
SETTLE_S = 15  # cold MotherDuck connection, then charts and maps painting


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=pathlib.Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, url in PAGES.items():
            page = browser.new_page(viewport={"width": 1440, "height": 2400}, device_scale_factor=2)
            sep = "&" if "?" in url else "?"
            page.goto(f"{url}{sep}embed=true", wait_until="networkidle", timeout=120_000)
            time.sleep(SETTLE_S)
            if name == "jmi-my-fit":
                box = page.get_by_placeholder("Paste your CV here")
                box.fill(SAMPLE_CV)
                box.press("Control+Enter")
                time.sleep(SETTLE_S)
            page.screenshot(path=args.out / f"{name}.png")
            print(f"captured {name}.png", flush=True)
            page.close()
        browser.close()


if __name__ == "__main__":
    main()
