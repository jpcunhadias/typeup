"""Figures for the 21 Jan lecture note: the unit square under a rotation."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.style.use("typeup.notes")
here = Path(__file__).parent

theta = np.pi / 6
R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
square = np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]], dtype=float)
turned = R @ square

fig, ax = plt.subplots(figsize=(3.6, 2.8))
ax.plot(*square, color="0.6", linestyle="--", label="unit square")
ax.plot(*turned, label=r"rotated by $\theta = 30^\circ$")
# labels beside the arrow tips, away from the square's edges
images = (
    (R[:, 0], r"$R_\theta\mathbf{e}_1$", (18, -4)),
    (R[:, 1], r"$R_\theta\mathbf{e}_2$", (-34, -12)),
)
for col, name, offset in images:
    ax.annotate(
        "", xy=(col[0], col[1]), xytext=(0, 0), arrowprops={"arrowstyle": "->", "color": "C1"}
    )
    ax.annotate(name, xy=(col[0], col[1]), xytext=offset, textcoords="offset points", fontsize=8.5)
ax.set_aspect("equal")
ax.set_xlim(-1.0, 1.4)
ax.set_ylim(-0.2, 1.6)
ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
fig.savefig(here / "LA-L02-rotation.pdf")
