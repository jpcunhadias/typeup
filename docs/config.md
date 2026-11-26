# Look and config

## Config file

typeup reads `~/.config/typeup/config.toml`, or `$XDG_CONFIG_HOME/typeup/config.toml`,
or the file named in `$TYPEUP_CONFIG`. Every key is optional:

```toml
mainfont = "Helvetica Neue"   # any font installed on your system
mainfontoptions = []          # fontspec options for it
fontsize = "11pt"
margin = "3cm"
linestretch = 1.25
file_links = true             # false: no absolute paths in PDFs

[legend]                      # see "Legend wording" below
added = "explained by the tutor"
```

The default font is TeX Gyre Heros, a Helvetica-like font that ships
with TeX Live. It is loaded by file name, so it works without installing
fonts system-wide. Maths uses Latin Modern Math.

## Colours and layout

All of the look is defined in one file, `src/typeup/data/notes-header.tex`:

- the colours of each box;
- heading styles;
- the gap between paragraphs (`\parskip`);
- the header and footer;
- table stripes;
- the code frame.

Change it there; `typeup path header` prints where the installed copy is.

## Legend wording

Inside the legend, each mark box says what it means. Change the wording
for one note in its front matter, or for all notes in the config file:

```yaml
---
legend-added: explained by the tutor
legend-your: my own notes
---
```

```toml
[legend]
added = "explained by the tutor"
your = "my own notes"
```

The keys are `added`, `your`, `unclear` and `source` (`legend-…` in
front matter). Front matter wins over the config file.

Values must have the right type (`file_links = false`, not `"false"`;
`mainfontoptions` a list of strings); a wrong one stops typeup with an
error naming the file and key.

Note: pandoc ignores `header-includes` in a note's front matter when a
header file is passed with `--include-in-header`, which typeup does. Put
LaTeX changes in `notes-header.tex` instead.
