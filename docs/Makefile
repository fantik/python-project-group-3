# Minimal makefile for Sphinx documentation

SPHINXBUILD ?= env LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 uv run --group docs sphinx-build
SOURCEDIR = source
BUILDDIR = build

.PHONY: help html clean

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)"

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"

clean:
	rm -rf "$(BUILDDIR)"
