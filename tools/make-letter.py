"""Render a cover letter to PDF in the CV's design.

    make letter        # letters/letter.toml -> ~/applications/<date>-<company>/
    .venv/bin/python tools/make-letter.py [letter.toml] [--archive DIR] [--preview]

The first run copies cv/letter.example.toml to letters/letter.toml: the one
working copy, edited for each application. Every run files the result in its
own folder, ~/applications/2026-09-27-acme/, holding the letter, the CV rendered
from cv/cv.toml as it stands, and a copy of both TOMLs exactly as sent, so there
is a record of what went to whom and when. The committed CV keeps its history in
git; this is the only place that says which version went with which letter.

Nothing about a letter is committed: letters/ is gitignored and the archive is
outside the repo, because a letter names the company you are applying to and
everything committed here is published. The script refuses a letter that git
would pick up. Name, contact line and headline come from cv/cv.toml, so the
letter and the CV always agree. Fields are documented in cv/letter.example.toml.
It fails on a second page, or while the example's [gaps] are still there.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import re
import shutil
import sys
import tomllib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CV = ROOT / "cv"
DEFAULT = ROOT / "letters" / "letter.toml"
cv = importlib.import_module("make-cv")   # same folder; reuse its render and folder rules


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("letter", type=Path, nargs="?", default=DEFAULT,
                    help="the letter's TOML (default: letters/letter.toml, gitignored)")
    ap.add_argument("--archive", type=Path, default=cv.ARCHIVE,
                    help="where each application gets its dated folder (default: ~/applications)")
    ap.add_argument("--preview", action="store_true", help="also write a PNG next to each PDF (needs pymupdf)")
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
    when = dt.date.fromisoformat(letter["date"]) if letter.get("date") else dt.date.today()
    folder = cv.application_folder(letter["company"], when, args.archive)
    data = tomllib.loads((CV / "cv.toml").read_text(encoding="utf-8"))
    person = data["person"]
    variant = letter.get("variant") or next(iter(data["variants"]))
    if variant not in data["variants"]:
        print(f"variant {variant!r} is not in cv/cv.toml: {', '.join(data['variants'])}", file=sys.stderr)
        return 1
    company = re.sub(r"[^A-Za-z0-9]+", "", letter["company"])
    out = folder / (letter.get("file") or f"{person['file_prefix']}-CoverLetter-{company}.pdf")
    cv_out = folder / f"{person['file_prefix']}-CV.pdf"
    if leaks := [p for p in (src, out, cv_out) if cv.publishable(p)]:
        print(f"{', '.join(str(p) for p in leaks)} would be committed, and this repo is public. "
              "Keep letters in letters/ (gitignored) or outside the repo.", file=sys.stderr)
        return 1

    if gaps := re.findall(r"\[[^\]]+\]", letter["body"]):
        print(f"fill in the example's gaps first: {'; '.join(' '.join(g.split()) for g in gaps)}", file=sys.stderr)
        return 1

    headline = data["variants"][variant]["headline"]
    paragraphs = [p for p in re.split(r"\n\s*\n", letter["body"].strip()) if p.strip()]
    date = when.strftime("%-d %B %Y")

    env = Environment(loader=FileSystemLoader(CV), autoescape=True)
    env.filters["md"] = lambda s: Markup(cv.md(s))
    page_html = env.get_template("letter.html.j2").render(
        p=data["person"], l=letter, headline=headline, date=date,
        paragraphs=paragraphs, fonts=(ROOT / "fonts").as_uri())

    folder.mkdir(parents=True, exist_ok=True)
    if src != folder / "letter.toml":
        shutil.copy(src, folder / "letter.toml")      # the text exactly as sent
    shutil.copy(CV / "cv.toml", folder / "cv.toml")   # the CV it went with
    tmp = folder / ".letter.html"
    tmp.write_text(page_html, encoding="utf-8")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp.as_uri(), wait_until="networkidle")
            page.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
            cv_ok = cv.render(browser, data, variant, cv_out, args.preview)
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
    return 1 if problems or not cv_ok else 0


if __name__ == "__main__":
    sys.exit(main())
