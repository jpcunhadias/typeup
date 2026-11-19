# Ideas for later

Not planned for a release. Written down so they aren't lost; open an
issue to discuss any of them.

## A study-session system around the notes

typeup covers one step: a typed note becomes a PDF. The steps around it
could become a product of their own:

- **Course sessions**: one working context per course, holding its notes,
  notation sheet, deadlines and where the student stands, so that each
  note continues the last one.
- **A schema** for that course state, such as books and pages, exercise
  sheets, exam rules and the notation table, so different tools can read
  and write it.
- **Tool integrations**, for example as MCP servers, that connect the
  course state to a calendar (lectures, study blocks), a task manager
  (deadlines, exercise sheets) and the notes folder.

Open questions:

- what the smallest useful schema is;
- whether it belongs in this repository or a separate one;
- how to keep personal data (timetables, grades) out of anything shared.

## Smaller ideas

- Relative file links that work from `pdf/` without absolute paths.
- A neutral default wording for the legend, with the current
  "helper typing for you" voice as an option.
- A `typeup new` command that creates a dated note from a template.
- HTML output with the same boxes, for reading on a phone.
