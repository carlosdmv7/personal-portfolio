"""Keep every Streamlit app this site links to awake.

    .venv/bin/pip install playwright && .venv/bin/playwright install chromium
    .venv/bin/python tools/wake-apps.py

Streamlit Community Cloud puts an app to sleep after a stretch without visits.
A sleeping app still answers HTTP 200, so the link check passes, but a
recruiter who clicks "Live app" gets a "Zzzz, this app has gone to sleep"
page and a button to press. That is a dead link in every way that matters.

A plain HTTP request does not count as a visit: the app only runs once a
browser opens its websocket. So this opens each app in a real browser, presses
the wake button if the app is asleep, and waits until the app itself renders.
It exits non-zero if any app does not come up, so the workflow goes red
instead of the visitor finding out.

The app list is read from the site's own HTML, so an app linked from a new
page is kept awake without editing this file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
APP_URL = re.compile(r"https://[a-z0-9-]+\.streamlit\.app/?")
SLEEP_TEXT = "has gone to sleep"
WAKE_BUTTON = "Yes, get this app back up"
# Streamlit's own root element; it exists only once the app is running.
APP_READY = '[data-testid="stApp"]'
BOOT_TIMEOUT_MS = 180_000  # a cold start installs the app's dependencies


def linked_apps() -> list[str]:
    urls: set[str] = set()
    for page in ROOT.glob("**/*.html"):
        if any(part.startswith(".") for part in page.relative_to(ROOT).parts):
            continue
        urls.update(u.rstrip("/") + "/" for u in APP_URL.findall(page.read_text(encoding="utf-8")))
    return sorted(urls)


def wake(browser, url: str) -> str:
    page = browser.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(5_000)
        was_asleep = SLEEP_TEXT in page.content()
        if was_asleep:
            page.get_by_role("button", name=WAKE_BUTTON).click()
        # The app renders inside an iframe on Community Cloud; look in every frame.
        deadline_ms, waited = BOOT_TIMEOUT_MS, 0
        while waited < deadline_ms:
            if any(f.query_selector(APP_READY) for f in page.frames):
                return "woken" if was_asleep else "awake"
            page.wait_for_timeout(5_000)
            waited += 5_000
        raise TimeoutError(f"not running after {BOOT_TIMEOUT_MS // 1000}s")
    finally:
        page.close()


def main() -> int:
    apps = linked_apps()
    if not apps:
        print("no Streamlit apps linked from the site", file=sys.stderr)
        return 1
    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in apps:
            try:
                print(f"ok    {wake(browser, url):6} {url}")
            except (PlaywrightError, TimeoutError) as e:
                failures += 1
                print(f"FAIL  {url}: {e}", file=sys.stderr)
        browser.close()
    print(f"\n{len(apps) - failures} of {len(apps)} app(s) running")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
