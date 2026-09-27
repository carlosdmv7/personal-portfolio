# Shortcuts for the jobs this repo actually repeats. Each one is a single
# script in tools/; this file only saves typing their paths.
#
#   make cv      regenerate the CV from cv/cv.toml (fails on 2 pages or ATS issues)
#   make check   everything to run before opening a PR
#   make og      regenerate the 1200x630 social cards
#   make letter  a cover letter in the CV's design, from letters/letter.toml
#                (gitignored; L=path/to/other.toml for another one)
#
# One-time setup:
#   python3 -m venv .venv && .venv/bin/pip install pillow jinja2 playwright pypdf
#   .venv/bin/playwright install chromium

PY := .venv/bin/python

.PHONY: cv check og letter

cv:
	$(PY) tools/make-cv.py

check:
	python3 tools/contrast-check.py
	$(PY) tools/render-check.py

og:
	$(PY) tools/make-og-images.py --out images

L ?= letters/letter.toml

letter:
	$(PY) tools/make-letter.py $(L) --preview
