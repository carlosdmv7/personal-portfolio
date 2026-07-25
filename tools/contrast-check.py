#!/usr/bin/env python3
"""WCAG 2.1 contrast checker for the portfolio palette."""
import sys


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(hexs):
    h = hexs.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


T = {
    "sand-100": "#F6E2B3", "amber-500": "#E7A84E", "rust-500": "#D96C2C",
    "teal-500": "#3E8E7E", "petrol-900": "#274C56", "surface": "#FDFAF4",
    "surface-2": "#F5EFE3", "border": "#E4D9C4", "ink": "#274C56",
    "ink-muted": "#5C7480", "rust-700": "#A8501F", "teal-700": "#2E6B5E",
    "rust-050": "#FBEADF", "teal-050": "#E4F0EC", "white": "#FFFFFF",
    # added tokens (not in the appendix, derived to fix measured violations)
    "teal-200": "#7FB3A4",    # from the diverging scale — graphical use on petrol
    "rust-300": "#DF844E",    # lightened rust — graphical use on petrol only
    "ink-muted-2": "#4E636D",  # secondary text on surface-2 / tints / sand
}

PAIRS = [
    # (fg, bg, min_ratio, what) — every pair the stylesheet actually produces
    # --- small text, needs 4.5:1 ---
    ("ink", "surface", 4.5, "body text"),
    ("ink", "surface-2", 4.5, "body text on cards"),
    ("ink", "sand-100", 4.5, "text on sand fill"),
    ("ink", "rust-050", 4.5, "text on rust tint"),
    ("ink", "teal-050", 4.5, "text on teal tint"),
    ("ink-muted", "surface", 4.5, "secondary text on page bg"),
    ("ink-muted-2", "surface", 4.5, "secondary text on page bg"),
    ("ink-muted-2", "surface-2", 4.5, "secondary text on cards"),
    ("ink-muted-2", "sand-100", 4.5, "secondary text on sand"),
    ("ink-muted-2", "rust-050", 4.5, "secondary text on rust tint"),
    ("ink-muted-2", "teal-050", 4.5, "secondary text on teal tint"),
    ("rust-700", "surface", 4.5, "links"),
    ("rust-700", "surface-2", 4.5, "links on cards"),
    ("rust-700", "rust-050", 4.5, "link / badge on rust tint"),
    ("teal-700", "surface", 4.5, "success text"),
    ("teal-700", "surface-2", 4.5, "success text on cards"),
    ("teal-700", "teal-050", 4.5, "success / badge on teal tint"),
    ("white", "rust-700", 4.5, "primary button label"),
    ("white", "teal-700", 4.5, "secondary button label"),
    ("sand-100", "petrol-900", 4.5, "band text"),
    ("white", "petrol-900", 4.5, "band value text"),
    # --- graphical (icons, dots, borders, rules), needs 3:1 ---
    ("rust-500", "surface", 3.0, "GRAPHIC icons / rules on page bg"),
    ("teal-500", "surface", 3.0, "GRAPHIC icons / fills on page bg"),
    ("teal-500", "surface-2", 3.0, "GRAPHIC icons on cards"),
    ("teal-200", "petrol-900", 3.0, "GRAPHIC pass-state dot on band"),
    ("amber-500", "petrol-900", 3.0, "GRAPHIC stale-state dot on band"),
    ("rust-300", "petrol-900", 3.0, "GRAPHIC fail-state dot on band"),
    ("sand-100", "rust-700", 3.0, "GRAPHIC underline on primary button"),
    # --- pairs the rules forbid; asserted never to be used as text ---
    ("teal-500", "petrol-900", 3.0, "FORBIDDEN — never paired"),
    ("rust-500", "petrol-900", 3.0, "FORBIDDEN — too dark on petrol, use rust-300"),
    ("rust-300", "surface", 3.0, "FORBIDDEN on light — petrol band only"),
    ("amber-500", "surface", 3.0, "FORBIDDEN as text — fills/charts only"),
    ("sand-100", "surface", 3.0, "FORBIDDEN as text — fills/charts only"),
]

def main():
    fail = 0
    print(f"{'foreground':<14} {'background':<12} {'ratio':>6}  {'min':>4}  {'':<4} note")
    print("-" * 80)
    for fg, bg, mn, note in PAIRS:
        r = ratio(T[fg], T[bg])
        ok = r >= mn
        flag = "PASS" if ok else "FAIL"
        if not ok and not note.startswith("FORBIDDEN"):
            fail += 1
        if note.startswith("FORBIDDEN"):
            flag = "n/a "
        print(f"{fg:<14} {bg:<12} {r:>6.2f}  {mn:>4.1f}  {flag:<4} {note}")
    print("-" * 80)
    print(f"{fail} violation(s)")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
