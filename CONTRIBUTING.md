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

## Branches and pull requests

`main` is protected: every change goes through a pull request, and CI
must pass before it can be merged.

1. Fork the repository (or, with write access, branch from `main`).
2. Name the branch after the change: `fix/table-head-at-page-break`,
   `feat/sans-maths-font`, `docs/config-examples`.
3. Open a pull request against `main`. Fill in the template: a
   `## Summary` of what changed and why, and a `## Test plan` with what
   you checked.
4. Keep the branch up to date with `main`. Pull requests are squash-merged,
   so the title becomes the commit on `main`: write it as a Conventional
   Commit.

Small, focused pull requests are reviewed fastest. For a larger change,
open an issue first so we can agree on the approach.

## Releases

The maintainer releases from `main`:

1. Move the "Unreleased" entries in `CHANGELOG.md` under a new version
   heading, and set `__version__` in `src/typeup/__init__.py`.
2. Merge that through a pull request, then tag it:
   `git tag v0.2.0 && git push origin v0.2.0`.
3. The release workflow checks that the tag matches `__version__` and
   creates the GitHub release with that version's changelog notes.

Versions follow [Semantic Versioning](https://semver.org/). A change to
how notes look is a minor version, even when nothing breaks.

## Code of conduct

Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md).
Security problems go through the [security policy](SECURITY.md), not
public issues.

## Licence

By contributing you agree that your contribution is licensed under the
[MIT licence](LICENSE).
