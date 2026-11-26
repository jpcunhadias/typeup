# Header metadata

Every page has a running header: course and label on the left, date on
the right. The same line appears in grey under the note's first `#`
heading. Each value comes from the first of these that sets it:

1. command-line flags: `--course`, `--label`, `--date`
2. the note's YAML front matter
3. the note's path and file name

```markdown
---
course: Linear Algebra
label: LA L01
date: 2026-01-14
---
```

A date written as `YYYY-MM-DD` is printed as "Wed 14 Jan 2026". Any other
text, such as `Week 3`, is printed as given. A `YYYY-MM-DD` date that is
not on the calendar (`2026-02-30`) stops the render with an error.

## The file-name convention

```
<Course>/notes/2026-01-14 LA L01 Vectors and spans.md
```

- **Date**: the file name starts with `YYYY-MM-DD` followed by a space
  (or `_`).
- **Label**: the next word, if it is a course code (2–4 letters, capital
  first, like `LA`, `HoA`), followed by:
  - a capital letter and a number (`L01` for a lecture, `E03` for an
    exercise class), giving "LA L01";
  - `Sheet <n>`, giving "LA Sheet 6";
  - anything else: the code alone ("LA").
- **Course**: the folder directly under a `courses/` folder (at any
  depth below it) or, failing that, the folder above a `notes/` folder. CamelCase is split into
  words, and short words other than the first stay lower case:
  `HistoryOfArt` becomes "History of Art".

A file without a leading date (a notation sheet, say) shows the course
alone.

## Combined PDFs

`typeup combine DIR` takes every note in `DIR` whose name starts with a
date, in date order. `--from` and `--until` (inclusive, `YYYY-MM-DD`)
narrow the range.

- Each note starts on a new page with its own header (flags, then its
  front matter, then its file name).
- The box numbers restart with each note.
- Each note is read on its own: its reference links (`[slides]`),
  footnotes (`[^1]`) and `legend-…` wording are its own, even when other
  notes use the same names. Links to `#anchors` point into the same note.
- The title page shows `--title` (default "Notes: <course>") and the
  date range, followed by a contents page that lists each note's
  first heading.
