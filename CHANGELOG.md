# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions
follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Roomier default spacing for easier reading: line spacing 1.25 (was 1.15),
  3 cm margins (was 2.3 cm), and a larger gap between paragraphs.

### Fixed

- A table that starts near the bottom of a page no longer leaves a copy
  of its head at the top of the next page, above its own heading.
- Lists, tables, formulas and code that follow a labelled line in a
  blockquote stay inside that mark box instead of falling out into a
  plain quote.
- Tables inside mark and content boxes keep their bottom rule and the same
  stripes as tables outside a box.
- Combined PDFs read each note on its own, so notes that use the same
  reference link or footnote names (`[slides]`, `[^1]`) keep their own
  targets and text, links to `#anchors` stay in their note, and a note's
  `legend-…` front matter applies to that note only.
- Source labels escape every LaTeX special character: `^`, `~` and `\`
  no longer break the build.
- Config values of the wrong type (`file_links = "false"`,
  `mainfontoptions = "Scale=0.9"`, `legend = 12`) are rejected with an
  error naming the file and key, as is a config file that isn't valid TOML.
- A `YYYY-MM-DD` date that is not on the calendar (`2026-02-30`,
  `2026-13-01`) stops the render with a clear error instead of printing a
  wrong header or crashing the filter; `--from` and `--until` must be real
  dates.

## [0.1.0] - 2026-11-19

### Added

- pandoc Lua filter and LaTeX header for typed-up notes:
  - `[Added]` / `[Your mark]` / `[Unclear]` / source-label mark boxes and
    inline `.unclear` spans;
  - numbered content boxes (definition, theorem, example, exercise,
    proof and others);
  - a "How to read this note" legend, its wording settable per note or
    in the config;
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
