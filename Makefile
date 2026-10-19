# Shortcuts for the jobs this repo actually repeats. Each one is a single
# script in tools/; this file only saves typing their paths.
#
#   make cv      regenerate the CV from cv/cv.toml (fails on 2 pages or ATS issues)
#   make check   everything to run before opening a PR
#   make brand   rewrite the token block of styles.css from the shared brand
#   make og      regenerate the 1200x630 social cards
#   make letter  a cover letter in the CV's design, from letters/letter.toml
#                (gitignored), filed in ~/cover-letters/<date>-<company>/
#
# One-time setup:  make setup

PY := .venv/bin/python

# The shared design system (github.com/carlosdmv7/brand), pinned by commit. The
# token block of styles.css is generated from it, and the tools import their
# palette from it. Bump the commit, run `make brand`, commit the diff.
BRAND_REF := git+https://github.com/carlosdmv7/brand@c3973c4a16bbbe57905ccc7d83a6cb94378b3bba
BRAND := uvx --from "$(BRAND_REF)" brand

.PHONY: setup cv check brand brand-check og letter

setup:
	python3 -m venv .venv
	.venv/bin/pip install pillow jinja2 playwright pypdf "brand @ $(BRAND_REF)"
	.venv/bin/playwright install chromium

cv:
	$(PY) tools/make-cv.py

check: brand-check
	$(PY) tools/render-check.py

# Every colour pair against WCAG AA, and styles.css against the brand. CI runs
# this target as is.
brand-check:
	$(BRAND) contrast
	$(BRAND) sync css styles.css --check

brand:
	$(BRAND) sync css styles.css

og:
	$(PY) tools/make-og-images.py --out images

L ?= letters/letter.toml

letter:
	$(PY) tools/make-letter.py $(L) --preview
