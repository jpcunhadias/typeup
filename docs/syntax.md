# Note syntax

A note is ordinary pandoc Markdown with maths in `$…$` and `$$…$$`.
typeup adds a few conventions on top of it.

## Marks: where a line came from

A blockquote line that starts with a bold label in brackets becomes a
coloured box:

```markdown
> **[Added]** The missing step: subtract $x$ from both sides.
> **[Your mark]** "check" written next to the name.
> **[Unclear: page 4, line 2]** Reads as $a_{ij}x_i$ or $a_{ij}x_j$.
> **[From the board, photo 21]** Any other label names a source.
```

| Label | Box | Meant for |
|---|---|---|
| `[Added]` | blue | what the typist added: a missing step, an explanation, a book reference |
| `[Your mark]` | amber | the writer's own margin notes, question marks, arrows |
| `[Unclear]`, `[Unclear: where]` | red | a reading that is a guess; the part after `:` says where in the original |
| `[anything else]` | grey | content from the source the label names |

- Several labelled lines in one blockquote become several boxes, in order.
- A paragraph that follows a labelled line in the same blockquote belongs
  to that box.
- A blockquote without a label stays an ordinary quote.

For a single uncertain symbol in running text, use an inline span:
`the pivot is [$x_2$?]{.unclear}`.

## Content boxes: what kind of text it is

```markdown
::: {.definition title="Dual problem"}
…
:::

::: {.theorem title="Weak duality"}
…
:::

::: proof
…
:::
```

Classes: `definition`, `theorem`, `proposition`, `lemma`, `corollary`,
`example`, `remark`, `exercise` and `proof`.

- All of them except `proof` share one counter (Definition 1, Example 2,
  Theorem 3), which restarts with each note in a combined PDF.
- `title` is optional and may contain `$maths$`.
- `proof` is unnumbered and ends with a box (□).
- Marks work inside content boxes.
- A div with any other class is left alone.

## The legend

A `::: legend` div draws a "How to read this note" frame. Put one short,
real example of each mark the note uses in it. Inside the legend, each box
title is followed by what the mark means:

```markdown
::: legend
> **[Added]** A linear combination is a weighted sum …
> **[Unclear: page 3, line 4]** Reads as $c_1 = 2$ or $c_1 = 3$.

Plain text is what was written in the lecture, tidied.
:::
```

To change those explanations, see [config.md](config.md#legend-wording).

## Page breaks

The filter keeps a heading, or a short lead-in line (one ending in ":", a
bold label, or under about 80 characters), on the same page as the
formula, list, table, code block or box it introduces. It can't see one
case: a lead-in that is the last line *inside* a box while what it
introduces comes after the box. Keep both inside the box, or both outside.

## Tables, code and long lines

- Pipe tables whose content adds up to more than about one line get
  column widths in proportion to their content, so cells wrap instead of
  running off the page. Table rows are striped.
- Inline `code` may break after `/ _ - .`, so long paths wrap.
- Code blocks get a light frame, with or without a language.
- A display equation longer than about 90 characters of LaTeX does not
  wrap. Split it with `aligned`.
- "Missing character" warnings mean the font lacks a symbol. Write it as
  maths instead (`$\to$` instead of →).

## Links to files

A link to a local file, written relative to the note
(`[the slides](../slides/week1.pdf)`), becomes an absolute file link. That
way it still opens from a PDF stored elsewhere (`pdf/`, a combined PDF).
The PDF then contains that absolute path, including your user name.
Use `--no-file-links` (or `file_links = false` in the
[config](config.md)) for PDFs you share: the links then stay as written.
Web links and `#anchors` are never changed.
