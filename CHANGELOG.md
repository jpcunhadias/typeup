# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions
follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-19

### Added

- pandoc Lua filter and LaTeX header for typed-up notes:
  - `[Added]` / `[Your mark]` / `[Unclear]` / source-label mark boxes and
    inline `.unclear` spans;
  - numbered content boxes (definition, theorem, example, exercise,
    proof and others);
  - a "How to read this note" legend;
  - keep-with-next page breaks;
  - striped tables with content-based column widths;
  - framed code blocks;
  - running headers with "page n / N" footers.
- `typeup render` and `typeup combine` (combined PDF of a date range, with
  a contents page and per-note headers).
- Header metadata from flags, YAML front matter or the
  `YYYY-MM-DD CODE L01 topic.md` file-name convention.
- Config file for font, size, margins, line spacing and file links;
  TeX Gyre Heros as the default font.
- `--no-file-links` to keep local paths out of shared PDFs.
- `typeup tex` (latexmk wrapper) and `homework` / `cheatsheet` LaTeX
  templates.
- `typeup.notes` matplotlib style.
- Example notes, their rendered PDFs, and CI that renders them.
