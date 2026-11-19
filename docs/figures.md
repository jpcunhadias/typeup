# Figures

typeup ships a matplotlib style with the fonts and colours of the PDF:

- a light grid;
- no top or right spine;
- the box colours as the colour cycle (Added blue, definition teal,
  Your-mark amber, theorem purple, example green, Unclear red, heading
  navy);
- vector PDF output.

```python
import matplotlib.pyplot as plt

plt.style.use("typeup.notes")  # needs typeup importable, e.g. uv run --with typeup
fig, ax = plt.subplots()
...
fig.savefig("figures/LA-L02-rotation.pdf")
```

Without the package importable, use the file path printed by
`typeup path mplstyle`.

Include the figure with a caption that says what to see:

```markdown
![The columns of $R_\theta$ are the images of $\mathbf{e}_1$ and
$\mathbf{e}_2$.](figures/LA-L02-rotation.pdf){width=70%}
```

Figures stay where they are written (no floating), centred, with a small
grey numbered caption. Paths are resolved relative to the note.
[`examples/LinearAlgebra/notes/figures/LA-L02.py`](../examples/LinearAlgebra/notes/figures/LA-L02.py)
is a complete example.
