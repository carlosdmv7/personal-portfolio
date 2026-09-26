"""Render every page at several widths and fail on anything a reader would see.

    .venv/bin/pip install playwright && .venv/bin/playwright install chromium
    .venv/bin/python tools/render-check.py [--shots DIR]

Checks each page at phone-to-desktop widths for horizontal overflow, images
that failed to load, and JavaScript errors, and exits non-zero on any of them.

It cannot tell you a layout *looks* wrong. A grid that drops a paragraph into
a 190px column overflows nothing and errors nowhere — that shipped once and
passed every automated check here. So --shots also saves a full-page
screenshot of each page at 1440px and 390px: open them before calling a
layout change done. Serves the repo itself on a spare port, so nothing else
needs to be running.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["", "projects/job-market-intelligence/", "projects/spanish-housing-radar/"]
WIDTHS = [1440, 1024, 768, 390, 360]


def serve() -> tuple[http.server.ThreadingHTTPServer, int]:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=Path, help="also save full-page screenshots here")
    args = ap.parse_args()
    if args.shots:
        args.shots.mkdir(parents=True, exist_ok=True)

    srv, port = serve()
    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in WIDTHS:
            for path in PAGES:
                page = browser.new_page(viewport={"width": width, "height": 900})
                errors: list[str] = []
                page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.goto(f"http://127.0.0.1:{port}/{path}", wait_until="networkidle")
                # walk the page so loading="lazy" images are actually requested
                height = page.evaluate("document.documentElement.scrollHeight")
                for y in range(0, height, 700):
                    page.evaluate(f"window.scrollTo(0, {y})")
                    page.wait_for_timeout(60)
                page.wait_for_timeout(400)

                scroll_w = page.evaluate("document.documentElement.scrollWidth")
                broken = page.evaluate(
                    "[...document.images].filter(i => i.complete && i.naturalWidth === 0)"
                    ".map(i => i.getAttribute('src'))")
                problems = []
                if scroll_w > width:
                    problems.append(f"page is {scroll_w}px wide")
                if broken:
                    problems.append(f"broken images {broken}")
                if errors:
                    problems.append(f"console errors {errors}")
                failures += bool(problems)
                if args.shots and width in (1440, 390):
                    page.evaluate("window.scrollTo(0, 0)")
                    name = (path.strip("/").split("/")[-1] or "home") + f"-{width}.png"
                    page.screenshot(path=str(args.shots / name), full_page=True)
                print(f"{'FAIL' if problems else 'ok  '} {width:4d}px /{path}"
                      + (f"  — {'; '.join(problems)}" if problems else ""))
                page.close()
        browser.close()
    srv.shutdown()
    print(f"\n{failures} failing render(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
