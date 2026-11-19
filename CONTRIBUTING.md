# Contributing

Thanks for helping. Bug reports with a small note that renders badly are
as useful as code.

## Set up

You need pandoc 3+, XeLaTeX (TeX Live), latexmk, pdftoppm and
[uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/jpcunhadias/typeup.git && cd typeup
uv sync --all-groups
uv run pre-commit install
```

## Check your change

```bash
make check      # ruff, ruff format --check, mypy, pytest
make examples   # figures, example PDFs, combined PDF, README screenshot
```

- Tests that need XeLaTeX are marked `tex`. `uv run pytest -m "not tex"`
  runs the fast ones (pandoc only).
- The filter tests (`tests/test_filter.py`) check pandoc's LaTeX output,
  so most filter changes can be tested without running TeX.
- For a layout change, run `make examples` and look at the pages. Attach
  a before/after screenshot to the pull request.
- CI runs the same checks on Ubuntu and renders the examples. The
  rendered PDFs are attached to each run as an artifact.

## Where things are

| Path | What |
|---|---|
| `src/typeup/data/marks.lua` | pandoc filter: marks, boxes, legend, keep-with-next, tables, links, header metadata |
| `src/typeup/data/notes-header.tex` | the look: colours, boxes, headers, headings |
| `src/typeup/notes.mplstyle` | matplotlib style (`typeup.notes`) |
| `src/typeup/meta.py` | header metadata from file names |
| `src/typeup/render.py` | pandoc calls for `render` and `combine` |
| `src/typeup/tex.py` | `typeup tex` (latexmk) |
| `examples/` | example notes and their rendered PDFs |
| `docs/` | user documentation |

## Conventions

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
  `feat(filter): …`, `fix(header): …`, `docs: …`.
- Add a line under "Unreleased" in `CHANGELOG.md` for anything a user
  would notice.
- Keep the Lua filter and the LaTeX header usable with plain pandoc. The
  Python package only finds the files and fills in metadata.
- Example notes must not contain personal data or links to local files.
  CI fails if a rendered PDF contains a local path.

## Licence

By contributing you agree that your contribution is licensed under the
[MIT licence](LICENSE).
