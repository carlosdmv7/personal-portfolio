"""Render a cover letter to PDF in the CV's design.

    make letter                  # letters/letter.toml -> letters/<file>.pdf
    .venv/bin/python tools/make-letter.py [path/to/letter.toml] [--preview]

The first run copies cv/letter.example.toml to letters/letter.toml. Edit that
copy for each application, run it again, and keep the PDF. letters/ is
gitignored on purpose: a letter names the company you are applying to, and
everything committed here is published. The script refuses a letter or a PDF
that git would pick up. Your name, contact line and headline come from
cv/cv.toml, so the letter and the CV always agree. The fields are documented
in cv/letter.example.toml. It fails on a second page.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CV = ROOT / "cv"
DEFAULT = ROOT / "letters" / "letter.toml"
cv = importlib.import_module("make-cv")   # same folder; reuse its markdown rule


def publishable(path: Path) -> bool:
    """True when the path is in this repo and git would not ignore it."""
    if not path.is_relative_to(ROOT):
        return False
    return subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", str(path)]).returncode != 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("letter", type=Path, nargs="?", default=DEFAULT,
                    help="the letter's TOML (default: letters/letter.toml, gitignored)")
    ap.add_argument("--preview", action="store_true", help="also write a PNG next to the PDF (needs pymupdf)")
    args = ap.parse_args()

    src = args.letter.expanduser().resolve()
    if src == DEFAULT and not src.exists():
        src.parent.mkdir(exist_ok=True)
        shutil.copy(CV / "letter.example.toml", src)
        print(f"created {src.relative_to(ROOT)} from the example: edit it, then run this again")
        return 0
    missing = [f for f in ("Archivo[wdth,wght].ttf", "PublicSans[wght].ttf")
               if not (ROOT / "fonts" / f).is_file()]
    if missing:
        print(f"fonts/ is missing {', '.join(missing)}: see README, Regenerating assets", file=sys.stderr)
        return 1

    letter = tomllib.loads(src.read_text(encoding="utf-8"))
    out = src.with_name(letter.get("file") or f"{src.stem}.pdf")
    if leaks := [p for p in (src, out) if publishable(p)]:
        print(f"{', '.join(str(p) for p in leaks)} would be committed, and this repo is public. "
              "Keep letters in letters/ (gitignored) or outside the repo.", file=sys.stderr)
        return 1

    if gaps := re.findall(r"\[[^\]]+\]", letter["body"]):
        print(f"fill in the example's gaps first: {'; '.join(' '.join(g.split()) for g in gaps)}", file=sys.stderr)
        return 1

    data = tomllib.loads((CV / "cv.toml").read_text(encoding="utf-8"))
    headline = next(iter(data["variants"].values()))["headline"]
    paragraphs = [p for p in re.split(r"\n\s*\n", letter["body"].strip()) if p.strip()]
    date = letter.get("date") or dt.date.today().strftime("%-d %B %Y")

    env = Environment(loader=FileSystemLoader(CV), autoescape=True)
    env.filters["md"] = lambda s: Markup(cv.md(s))
    page_html = env.get_template("letter.html.j2").render(
        p=data["person"], l=letter, headline=headline, date=date,
        paragraphs=paragraphs, fonts=(ROOT / "fonts").as_uri())

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
