# LaTeX documents

For documents where the layout matters more than in a note, such as a
typed homework submission or a draft of an exam formula sheet, typeup has
two templates and a compile command.

```bash
typeup template homework hw1.tex      # or: cheatsheet
typeup tex hw1.tex --png
```

## `typeup tex`

- Runs latexmk. Aux files go to `build/` beside the source, and the PDF
  is copied next to the `.tex`.
- Picks the engine from a `% !TEX program = …` line if there is one; a
  file that loads fontspec or unicode-math gets XeLaTeX; anything else
  gets pdfLaTeX. `--engine pdf|xe|lua` overrides this.
- Adds `-shell-escape` when the file loads minted.
- On failure, prints the first errors with file and line, instead of
  the whole log.
- `--name NAME` sets the output file name (for submissions with a
  required name); `--png` writes page previews to `build/preview/`;
  `--clean` removes `build/`.

## Templates

- `homework`: one `problem` environment per task, numbered to match the
  sheet, with `task` and `solution` parts. It also has boxed code
  listings (`\begin{code}{Python}`, `\codefile{file.R}{R}`) and
  pseudocode. Fill in `\course`, `\sheet`, `\due`, `\student`.
- `cheatsheet`: landscape A4, three columns, 8 pt, one box per topic.
  Check your exam's rules before shrinking the font.
