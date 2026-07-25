#!/usr/bin/env python3
"""Render the raster icons from the same geometry as images/favicon.svg.

  apple-touch-icon.png  180x180  (iOS home screen — needs an opaque field)
  favicon-32.png         32x32   (legacy browsers that ignore the SVG)
  favicon-192.png       192x192  (Android / PWA)

Usage:  python3 tools/make-icons.py --out images
Requires: pillow
"""
from __future__ import annotations

import argparse
import pathlib

from PIL import Image, ImageDraw

PETROL = "#274C56"
SAND = "#F6E2B3"
RUST = "#D96C2C"
TEAL = "#3E8E7E"

# favicon.svg geometry, in its 64x64 viewBox
SERIES = [(13, 44), (26, 31), (36, 38), (50, 19)]
POINT = (50, 19, 5.5)
BASELINE = ((13, 52), (50, 52))
RADIUS = 14


def render(size: int, supersample: int = 8) -> Image.Image:
    s = size * supersample
    k = s / 64  # viewBox -> pixel scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=RADIUS * k, fill=PETROL)

    d.line([(x * k, y * k) for x, y in SERIES], fill=SAND, width=int(6 * k),
           joint="curve")
    # round caps
    for x, y in (SERIES[0], SERIES[-1]):
        r = 3 * k
        d.ellipse([x * k - r, y * k - r, x * k + r, y * k + r], fill=SAND)

    px, py, pr = POINT
    d.ellipse([(px - pr) * k, (py - pr) * k, (px + pr) * k, (py + pr) * k], fill=RUST)

    (bx1, by1), (bx2, by2) = BASELINE
    d.line([(bx1 * k, by1 * k), (bx2 * k, by2 * k)], fill=TEAL, width=int(3.5 * k))
    for x, y in ((bx1, by1), (bx2, by2)):
        r = 1.75 * k
        d.ellipse([x * k - r, y * k - r, x * k + r, y * k + r], fill=TEAL)

    return img.resize((size, size), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("images"))
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    for name, size, opaque in [
        ("apple-touch-icon", 180, True),   # iOS composites onto white otherwise
        ("favicon-192", 192, False),
        ("favicon-32", 32, False),
    ]:
        img = render(size)
        if opaque:
            flat = Image.new("RGB", img.size, PETROL)
            flat.paste(img, mask=img.split()[3])
            img = flat
        path = a.out / f"{name}.png"
        img.save(path, optimize=True)
        print(f"{path}  {size}x{size}  {path.stat().st_size // 1024 or 1} KB")


if __name__ == "__main__":
    main()
