.PHONY: all papers clean check install-hooks help

all: papers

# Build every manuscript under manuscripts/. Convention: a manuscript is a
# directory `manuscripts/<slug>/` containing `<slug>.tex`. The built PDF is
# placed next to its source; the latexmk cache stays in `<slug>/_build/`.

PAPER_DIRS  := $(wildcard manuscripts/*)
PAPER_PDFS  := $(foreach d,$(PAPER_DIRS),$(d)/$(notdir $(d)).pdf)
BUILD_DIRS  := $(foreach d,$(PAPER_DIRS),$(d)/_build)

papers: $(PAPER_PDFS)

manuscripts/%.pdf: manuscripts/%.tex
	@mkdir -p $(dir $@)_build
	cd ./$(dir $@) && latexmk -pdf -outdir=_build -interaction=nonstopmode $(notdir $<)
	@cp $(dir $@)_build/$(notdir $@) $@
	@echo "PDF: $@"

clean:
	rm -rf $(BUILD_DIRS)
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

install-hooks:
	git config core.hooksPath .githooks
	@echo "git hooks path set to .githooks/"

# Sanity-check: every tracked Python file parses without syntax errors.
PY_FILES := $(shell git ls-files '*.py')

check:
	@python3 -c "import sys; [compile(open(f).read(), f, 'exec') for f in sys.argv[1:]]" $(PY_FILES)
	@echo "All tracked .py files parse cleanly."
	@python3 scripts/check_licenses.py

help:
	@echo "Available targets:"
	@echo "  papers        — build every manuscript PDF under manuscripts/"
	@echo "  clean         — remove all build artefacts (_build/, __pycache__/)"
	@echo "  check         — sanity check (currently: all tracked .py parse)"
	@echo "  install-hooks — enable .githooks/pre-commit (one-time per clone)"
