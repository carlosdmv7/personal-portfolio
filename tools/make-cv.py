"""Render every CV variant in cv/cv.toml to PDF, from one template.

    .venv/bin/pip install jinja2 playwright pypdf && .venv/bin/playwright install chromium
    .venv/bin/python tools/make-cv.py [--preview]

One source, several emphases: a fact changes in cv.toml once and every PDF
agrees. Each variant must fit on one A4 page; the script fails if one spills
onto a second, rather than shipping a CV whose last line sits alone on page 2.
It also reads each PDF back the way an applicant-tracking system does and fails
if a heading or a key term does not come out as a plain word (see ats_problems).
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


HEADINGS = ["EXPERIENCE", "PROJECTS", "SKILLS", "EDUCATION", "LANGUAGES"]
KEY_TERMS = ["Snowflake", "dbt", "Python", "SQL", "Prefect", "Power BI", "Streamlit", "AWS"]


def ats_problems(pdf: Path) -> list[str]:
    """What a parser would get wrong. Each of these shipped once and looked fine:
    letter-spaced headings extracted as "E XP E R I E N C E", the "fl" ligature
    turned Snowflake into "Snowﬂake" (invisible to a keyword search), and CSS
    separators left "relocation·carlosdmv7@…" with no space."""
    from pypdf import PdfReader
    text = PdfReader(str(pdf)).pages[0].extract_text()
    problems = []
    if lig := sorted({c for c in text if "\ufb00" <= c <= "\ufb06"}):
        problems.append(f"ligature glyphs {lig}")
    problems += [f"heading {h!r} not extractable" for h in HEADINGS if h not in text]
    problems += [f"key term {k!r} not extractable" for k in KEY_TERMS if k not in text]
    if re.search(r"\S·|·\S", text):
        problems.append("separator without spaces")
    return problems


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
            # Chromium stamps the render time into /CreationDate and /ModDate, the
            # only bytes that differ between two renders of the same content. Pin
            # them (same length, so the xref offsets stay valid) and an unchanged
            # CV regenerates byte-identical: `git status` then shows a change only
            # when there is one.
            out.write_bytes(re.sub(rb"(/(?:CreationDate|ModDate) \(D:)\d{14}",
                                   rb"\g<1>20260101000000", out.read_bytes()))
            pages = len(re.findall(rb"/Type\s*/Page[^s]", out.read_bytes()))
            ats = ats_problems(out)
            ok = pages == 1 and not ats
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {out.relative_to(ROOT)}  {pages} page(s)  "
                  f"{out.stat().st_size / 1024:.0f} KB" + (f"  ATS: {'; '.join(ats)}" if ats else "  ATS: ok"))
            if args.preview:
                page.set_viewport_size({"width": 794, "height": 1123})  # A4 at 96 dpi
                page.emulate_media(media="print")
                page.screenshot(path=str(out.with_suffix(".png")), full_page=True)
            page.close()
        browser.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
