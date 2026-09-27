"""Render a cover letter to PDF in the CV's design.

    .venv/bin/python tools/make-letter.py ~/cover-letters/acme.toml [--preview]

The letter's own words live in a TOML *outside this repo*: everything here is
published, and a letter names the company you are applying to. The script
refuses a letter inside the repo for that reason. Your name, contact line and
headline come from cv/cv.toml, so the letter and the CV always agree.

    company  = "Acme"                      # required
    role     = "Analytics Engineer"        # optional, shown beside the company
    date     = "29 September 2026"         # optional, defaults to today
    greeting = "Dear Acme Data Team,"      # required
    body     = \"\"\"First paragraph.

    Second paragraph, with **bold** if you need it.\"\"\"
    sign_off = "Best regards,"             # optional
    file     = "Carlos-De-Manuel-Cover-Letter-Acme.pdf"   # optional

The PDF is written next to the TOML. It fails on a second page.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import re
import sys
import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CV = ROOT / "cv"
cv = importlib.import_module("make-cv")   # same folder; reuse its markdown and font rules


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("letter", type=Path, help="the letter's TOML, kept outside this repo")
    ap.add_argument("--preview", action="store_true", help="also write a PNG next to the PDF (needs pymupdf)")
    args = ap.parse_args()

    src = args.letter.expanduser().resolve()
    if src.is_relative_to(ROOT):
        print(f"{src} is inside the repo, and everything here is published. "
              "Keep letters in a folder of your own, e.g. ~/cover-letters/.", file=sys.stderr)
        return 1
    missing = [f for f in ("Archivo[wdth,wght].ttf", "PublicSans[wght].ttf")
               if not (ROOT / "fonts" / f).is_file()]
    if missing:
        print(f"fonts/ is missing {', '.join(missing)}: see README, Regenerating assets", file=sys.stderr)
        return 1

    letter = tomllib.loads(src.read_text(encoding="utf-8"))
    data = tomllib.loads((CV / "cv.toml").read_text(encoding="utf-8"))
    headline = next(iter(data["variants"].values()))["headline"]
    paragraphs = [p for p in re.split(r"\n\s*\n", letter["body"].strip()) if p.strip()]
    date = letter.get("date") or dt.date.today().strftime("%-d %B %Y")

    env = Environment(loader=FileSystemLoader(CV), autoescape=True)
    env.filters["md"] = lambda s: Markup(cv.md(s))
    page_html = env.get_template("letter.html.j2").render(
        p=data["person"], l=letter, headline=headline, date=date,
        paragraphs=paragraphs, fonts=(ROOT / "fonts").as_uri())

    out = src.with_name(letter.get("file") or f"{src.stem}.pdf")
    tmp = src.with_name(f".{src.stem}.html")
    tmp.write_text(page_html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp.as_uri(), wait_until="networkidle")
            page.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
            browser.close()
    finally:
        tmp.unlink(missing_ok=True)
    if args.preview:
        # rasterise the PDF itself: a page screenshot would drop the @page margins
        import pymupdf
        pymupdf.open(out)[0].get_pixmap(dpi=110).save(out.with_suffix(".png"))

    pages = len(re.findall(rb"/Type\s*/Page[^s]", out.read_bytes()))
    from pypdf import PdfReader
    text = PdfReader(str(out)).pages[0].extract_text()
    problems = [f"{pages} pages"] if pages != 1 else []
    if lig := sorted({c for c in text if "ﬀ" <= c <= "ﬆ"}):
        problems.append(f"ligature glyphs {lig}")
    words = len(" ".join(paragraphs).split())
    print(f"{'FAIL' if problems else 'ok  '} {out}  {pages} page(s)  {words} words"
          + (f"  {'; '.join(problems)}" if problems else ""))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
