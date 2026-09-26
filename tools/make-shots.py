#!/usr/bin/env python3
"""Downscale the Job Market Intelligence app screenshots into images/jmi/.

The source PNGs live in that project's repo (docs/img/, all captured from the
live warehouse) at 2880px wide and ~250 KB each. The case-study page never
renders them wider than ~840 CSS px, so they ship at 1440px in WebP — the whole
set lands around 400 KB instead of 1.7 MB.

Trailing background is cropped: several screens end in a long run of empty page
below the content, which reads as a broken image at the bottom of a figure.

    python3 tools/make-shots.py --src ~/projects/job-market-intelligence/docs/img

Requires: pillow.
"""
from __future__ import annotations

import argparse
import pathlib

from PIL import Image

WIDTH = 1440
QUALITY = 82
BOTTOM_MARGIN = 28  # px of background kept below the last content row

# The source repo ships seven screens; the case study shows three. Every extra
# screenshot is a re-capture and a caption rewrite each time the app changes,
# and the case study is written to survive that — the live app is one click
# away and carries the current numbers. What is kept is the one that shows the
# shape of the data (home), the one the pipeline exists to produce (my-fit),
# and the one that makes the source-legibility argument (market-detail).
# Pass --only to override.
USED = ["home", "my-fit", "market-detail"]


def trim_bottom(im: Image.Image) -> Image.Image:
    """Drop trailing rows that are entirely the page background colour."""
    bg = im.getpixel((4, im.height - 4))
    px = im.load()
    step = max(1, im.width // 240)  # sample columns; exact scan is not worth it
    last = im.height - 1
    while last > im.height // 3:
        if any(px[x, last] != bg for x in range(0, im.width, step)):
            break
        last -= 1
    return im.crop((0, 0, im.width, min(im.height, last + BOTTOM_MARGIN)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=pathlib.Path,
                    help="a project repo's docs/img directory")
    ap.add_argument("--out", default=pathlib.Path("images/jmi"), type=pathlib.Path)
    ap.add_argument("--only", nargs="*", default=USED,
                    help="stems to convert; defaults to the ones the case study renders")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    for f in sorted(f for f in args.src.glob("*.png") if f.stem in set(args.only)):
        im = trim_bottom(Image.open(f).convert("RGB"))
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
        dst = args.out / f"{f.stem}.webp"
        im.save(dst, "WEBP", quality=QUALITY, method=6)
        print(f"{dst}  {im.width}x{im.height}  {dst.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
