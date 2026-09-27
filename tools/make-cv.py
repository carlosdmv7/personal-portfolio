"""Render every CV variant in cv/cv.toml to PDF, from one template.

    .venv/bin/pip install jinja2 playwright && .venv/bin/playwright install chromium
    .venv/bin/python tools/make-cv.py [--preview]

One source, several emphases: a fact changes in cv.toml once and every PDF
agrees. Each variant must fit on one A4 page; the script fails if one spills
onto a second, rather than shipping a CV whose last line sits alone on page 2.
--preview also writes a PNG of each page next to the PDF, to look at.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CV = ROOT / "cv"


def md(text: str) -> str:
    """The one bit of markup cv.toml uses: **bold**."""
    # collapse layout whitespace only: a non-breaking space in cv.toml ("23\u00a0to\u00a0180")
    # is there to keep a figure on one line, and str.split() would eat it
    flat = re.sub(r"[ \t\r\n]+", " ", text).strip()
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(flat))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="also write a PNG per variant")
    args = ap.parse_args()

    data = tomllib.loads((CV / "cv.toml").read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(CV), autoescape=True)
    env.filters["md"] = lambda s: __import__("markupsafe").Markup(md(s))
    # .j2, not .html: Pages would publish a .html as a page, and the link
    # checker would try to resolve its {{ placeholders }} as URLs.
    tpl = env.get_template("template.html.j2")

    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, v in data["variants"].items():
            jobs = []
            for job in data["jobs"]:
                wanted = v["experience"] if job["id"] == "resrg" else list(job["bullets"])
                jobs.append({**job, "picked": [job["bullets"][k] for k in wanted]})
            page_html = tpl.render(
                p=data["person"], v=v, jobs=jobs, x=data["extras"],
                projects=[data["projects"][k] for k in v["projects"]],
                skills=[data["skills"][k] for k in v["skills"]],
                education=data["education"], fonts=(ROOT / "fonts").as_uri(),
            )
            src = CV / f".{name}.html"          # gitignored; kept for debugging
            src.write_text(page_html, encoding="utf-8")

            page = browser.new_page()
            page.goto(src.as_uri(), wait_until="networkidle")
            out = CV / v["file"]
            out.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
            pages = len(re.findall(rb"/Type\s*/Page[^s]", out.read_bytes()))
            ok = pages == 1
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {out.relative_to(ROOT)}  {pages} page(s)  "
                  f"{out.stat().st_size / 1024:.0f} KB")
            if args.preview:
                page.set_viewport_size({"width": 794, "height": 1123})  # A4 at 96 dpi
                page.emulate_media(media="print")
                page.screenshot(path=str(out.with_suffix(".png")), full_page=True)
            page.close()
        browser.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
