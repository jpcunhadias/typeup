# make examples: figures, one PDF per example note, the combined PDF and
# the README screenshot. Needs uv, pandoc 3+, XeLaTeX and pdftoppm.
NOTES := examples/LinearAlgebra/notes

.PHONY: examples figures notes combined screenshot check clean

examples: figures notes combined screenshot

figures:
	for f in $(NOTES)/figures/*.py; do uv run --group examples python "$$f" || exit 1; done

notes:
	uv run typeup render --no-file-links $(NOTES)/2*.md

combined:
	uv run typeup combine --no-file-links $(NOTES) --title "Linear Algebra: notes for the first test" \
	  -o $(NOTES)/pdf/LA-combined.pdf

screenshot:
	pdftoppm -png -r 110 -f 1 -l 1 -singlefile "$(NOTES)/pdf/2026-01-14 LA L01 Vectors and spans.pdf" docs/images/page-1

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .
	uv run pytest

clean:
	rm -f $(NOTES)/pdf/*.pdf
