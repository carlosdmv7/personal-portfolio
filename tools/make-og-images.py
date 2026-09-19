#!/usr/bin/env python3
"""Render the 1200x630 og:image cards for the site, in the shared palette.

Fonts are not vendored. Fetch them once into ./fonts (or pass --fonts):

    mkdir -p fonts && cd fonts
    curl -sSLO "https://github.com/google/fonts/raw/main/ofl/archivo/Archivo%5Bwdth,wght%5D.ttf"
    curl -sSLO "https://github.com/google/fonts/raw/main/ofl/publicsans/PublicSans%5Bwght%5D.ttf"
    curl -sSLO "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Medium.ttf"

Then:  python3 tools/make-og-images.py --out images
Requires: pillow
"""
from __future__ import annotations

import argparse
import pathlib

from PIL import Image, ImageDraw, ImageFont

# --- palette (authoritative tokens; keep in sync with styles.css :root) -------
PETROL = "#274C56"
SAND = "#F6E2B3"
AMBER = "#E7A84E"
RUST = "#D96C2C"
TEAL = "#3E8E7E"
TEAL_200 = "#7FB3A4"
INK_MUTED = "#5C7480"
CATEGORICAL = [PETROL, RUST, TEAL, AMBER, INK_MUTED]

W, H = 1200, 630
PAD = 82

CARDS = {
    "og-home": {
        "eyebrow": "CARLOS DE MANUEL  ·  ANALYTICS ENGINEER",
        "headline": "Data you can trust:\nmodelled, tested,\ndocumented.",
        "sub": "dbt · Snowflake · DuckDB · Prefect · Python. I build the layer "
               "between raw data and decisions.",
        "chips": ["800M+ ROWS IN SNOWFLAKE", "130+ GOVERNED KPIS", "200+ USERS"],
    },
    "og-job-market-intelligence": {
        "eyebrow": "CASE STUDY  ·  JOB MARKET INTELLIGENCE ENGINE",
        "headline": "Visa sponsorship\nyou can audit.",
        "sub": "Every posting's company is joined against the official IND register of "
               "recognised sponsors. Each match carries a KvK number — so any flag is "
               "checkable against a public register.",
        "chips": ["12,797 IND SPONSORS", "9 DBT MODELS", "45 DATA TESTS", "€0 / MONTH"],
    },
    "og-spanish-housing-radar": {
        "eyebrow": "CASE STUDY  ·  SPANISH HOUSING RADAR",
        "headline": "Under-priced,\nquantified.",
        "sub": "An Opportunity Score built from the z-score of €/m² against the finest "
               "local benchmark that still has enough comparables — neighbourhood, "
               "district, then city.",
        "chips": ["16 DBT MODELS", "104 DATA TESTS", "3 SOURCES", "6 APP PAGES"],
    },
}


def load(fonts: pathlib.Path, filename: str, size: int, weight: float | None = None):
    f = ImageFont.truetype(str(fonts / filename), size)
    if weight is not None:
        try:
            axes = [a[2] for a in f.get_variation_axes()]  # start with defaults
            names = [
                (a[3] if len(a) > 3 else b"").decode(errors="ignore").lower()
                if isinstance(a[3] if len(a) > 3 else b"", bytes) else ""
                for a in f.get_variation_axes()
            ]
            for i, ax in enumerate(f.get_variation_axes()):
                # 'wght' axis is the one whose range spans typical weight values
                lo, hi = ax[0], ax[1]
                if lo <= 400 <= hi and hi >= 700:
                    axes[i] = weight
            f.set_variation_by_axes(axes)
        except Exception:
            pass  # static font, or Pillow without variation support
    return f


def tracked(draw, xy, text, font, fill, tracking=3.0):
    """Draw text with letter-spacing; returns the advance width."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x - xy[0] - tracking


def wrap(draw, text, font, max_w):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            trial = f"{cur} {w}".strip()
            if draw.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def render(name: str, spec: dict, fonts: pathlib.Path, out: pathlib.Path):
    img = Image.new("RGB", (W, H), PETROL)
    d = ImageDraw.Draw(img)

    display = load(fonts, "Archivo[wdth,wght].ttf", 78, weight=700)
    body = load(fonts, "PublicSans[wght].ttf", 25, weight=400)
    mono = load(fonts, "IBMPlexMono-Medium.ttf", 17)
    mono_sm = load(fonts, "IBMPlexMono-Medium.ttf", 15)

    # top hairline in the categorical scale — the palette signature
    seg = W / len(CATEGORICAL)
    for i, c in enumerate([RUST, AMBER, TEAL, TEAL_200, SAND]):
        d.rectangle([i * seg, 0, (i + 1) * seg, 7], fill=c)

    head_lines = wrap(d, spec["headline"], display, W - 2 * PAD)
    sub_lines = wrap(d, spec["sub"], body, W - 2 * PAD - 30)

    # centre the type block in the space between the top rule and the chip row
    block_h = 30 + 45 + len(head_lines) * 86 + 14 + len(sub_lines) * 36
    y = 7 + max(PAD - 26, (H - 96 - 7 - block_h) // 2)

    # eyebrow, in mono, teal-200 on petrol (graphical label, tracked)
    tracked(d, (PAD, y), spec["eyebrow"], mono_sm, TEAL_200, tracking=2.4)
    y += 30

    # rust accent rule — the one loud element
    d.rectangle([PAD, y, PAD + 88, y + 5], fill=RUST)
    y += 45

    # headline, Archivo bold, sand on petrol (7.3:1)
    for line in head_lines:
        d.text((PAD, y), line, font=display, fill=SAND)
        y += 86
    y += 14

    # sub, Public Sans, sand on petrol
    for line in sub_lines:
        d.text((PAD, y), line, font=body, fill=SAND)
        y += 36

    # chips along the bottom, mono, sand text in outlined pills
    cy = H - PAD + 4
    cx = PAD
    for chip in spec["chips"]:
        tw = d.textlength(chip, font=mono)
        d.rounded_rectangle([cx, cy, cx + tw + 30, cy + 38], radius=19,
                            outline=TEAL_200, width=2)
        d.text((cx + 15, cy + 10), chip, font=mono, fill=SAND)
        cx += tw + 42

    # signature, right-aligned in the gap above the chip row
    url = "carlosdmv7.github.io/personal-portfolio"
    d.text((W - PAD - d.textlength(url, font=mono_sm), cy - 38), url,
           font=mono_sm, fill=TEAL_200)

    path = out / f"{name}.png"
    img.save(path, optimize=True)
    print(f"{path}  {W}x{H}  {path.stat().st_size // 1024} KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", type=pathlib.Path, default=pathlib.Path("fonts"))
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("images"))
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    for name, spec in CARDS.items():
        render(name, spec, a.fonts, a.out)


if __name__ == "__main__":
    main()
