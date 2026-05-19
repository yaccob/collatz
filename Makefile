.PHONY: all paper paper-clean check-py help

all: paper

# Build the t_minus manuscript PDF. Build artefacts go into manuscripts/t_minus/_build/.
PAPER_DIR  := $(CURDIR)/manuscripts/t_minus
PAPER_BASE := obstructions

paper:
	@mkdir -p "$(PAPER_DIR)/_build"
	cd "$(PAPER_DIR)" && latexmk -pdf -outdir=_build -interaction=nonstopmode $(PAPER_BASE).tex
	@echo ""
	@echo "PDF: $(PAPER_DIR)/_build/$(PAPER_BASE).pdf"

paper-clean:
	rm -rf "$(PAPER_DIR)/_build"

# Parse every tracked .py file with py_compile. Catches syntax errors
# introduced by sweeping refactors.
check-py:
	@FAILED=""; \
	for f in $$(git ls-files '*.py'); do \
		python3 -m py_compile "$$f" 2>/dev/null || FAILED="$$FAILED $$f"; \
	done; \
	if [ -n "$$FAILED" ]; then \
		echo "Files failing to parse:"; \
		for f in $$FAILED; do echo "  $$f"; done; \
		exit 1; \
	else \
		echo "All tracked .py files parse cleanly."; \
	fi

help:
	@echo "Available targets:"
	@echo "  paper       — build the t_minus manuscript PDF"
	@echo "  paper-clean — remove build artefacts (_build/)"
	@echo "  check-py    — py_compile sanity check across all tracked .py"
