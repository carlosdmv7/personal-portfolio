#!/usr/bin/env python3
"""Crop and downscale the app screenshots the case studies show.

The sources are 2x captures of a 1440px-wide viewport (tools/capture-app.py),
taller than any figure needs. Each figure is cut at a band of empty page
background right below a finished section, never through a chart or a table:
a figure that ends on a heading with nothing under it reads as a broken image.

Two framings. A lead figure spans the page, so it keeps the app's own top bar
and ships at 1440px. A figure that sits beside the prose drops the bar and the
side margins, so the content is as large as the narrower column allows, and
ships at the crop's CSS width, about twice what it renders at.

    .venv/bin/python tools/capture-app.py --out /tmp/shots
    python3 tools/make-shots.py --src /tmp/shots

Requires: pillow.
"""
from __future__ import annotations

import argparse
import pathlib

from PIL import Image

QUALITY = 82
SCALE = 2  # the captures' device scale factor

LEAD = 1440
SIDE = (64, 1376)  # the app's content column, a little of its margin kept

# published path -> (source capture, (left, top, right, bottom) in CSS px).
# Every bottom edge is inside a band of plain background; re-check them after
# a recapture, because the app's layout moves with its data.
SHOTS: dict[str, tuple[str, tuple[int, int, int, int]]] = {
    "jmi/home.webp": ("jmi-home", (0, 0, LEAD, 1100)),
    "jmi/my-fit.webp": ("jmi-my-fit", (SIDE[0], 510, SIDE[1], 1470)),
    "jmi/market-detail.webp": ("jmi-market-detail", (SIDE[0], 60, SIDE[1], 1420)),
    "shr/home.webp": ("shr-home", (0, 0, LEAD, 1085)),
    "shr/opportunities.webp": ("shr-opportunities", (SIDE[0], 64, SIDE[1], 1125)),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=pathlib.Path,
                    help="directory holding the captures, named as in SHOTS")
    ap.add_argument("--out", default=pathlib.Path("images"), type=pathlib.Path)
    args = ap.parse_args()

    for dst_name, (src_name, box) in SHOTS.items():
        im = Image.open(args.src / f"{src_name}.png").convert("RGB")
        im = im.crop(tuple(v * SCALE for v in box))
        width = box[2] - box[0]
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        dst = args.out / dst_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "WEBP", quality=QUALITY, method=6)
        print(f"{dst}  {im.width}x{im.height}  {dst.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
