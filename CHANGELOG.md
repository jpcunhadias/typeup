# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions
follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- The legend explains each mark in neutral wording ("added while typing
  up", "a note the writer made in the margin", "an uncertain reading").
  The `legend-*` keys still change it.
- The course in the header comes from a `courses/<Course>/` folder first,
  at any depth below it, and only then from the folder above `notes/`.

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

[Unreleased]: https://github.com/jpcunhadias/typeup/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jpcunhadias/typeup/releases/tag/v0.1.0
