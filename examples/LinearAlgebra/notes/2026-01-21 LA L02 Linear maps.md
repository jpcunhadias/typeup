# Linear Algebra, lecture of 21 Jan: linear maps and matrices

Typed on 22 Jan 2026 from the handwritten note of 21 Jan (5 pages).

::: legend
> **[Added]** The columns of $A$ are where the unit vectors go …
> **[Unclear: page 2, line 7]** The sign in front of $\sin\theta$.

Plain text is what was written in the lecture, tidied. The figure was drawn
from the formula in Example 3.
:::

## What this lecture is about

Functions between vector spaces that keep linear combinations intact,
and why each of them is a matrix. It continues the last lecture: $A\mathbf{x}$
is the linear combination of the columns of $A$ with weights $x_1, \dots, x_n$.

## Where to learn it

| Source | Pages | What is there |
|---|---|---|
| Course textbook, ch. 2 | pp. 31–40 | linear maps, the standard matrix |
| Course textbook, ch. 2 | pp. 41–45 | rotations and reflections |

Used in: Exercise sheet 2, task 1.

## 2.1 Linear maps

::: {.definition title="Linear map"}
A function $T\colon \mathbb{R}^n \to \mathbb{R}^m$ is *linear* if for all
vectors $\mathbf{x}, \mathbf{y}$ and scalars $c$:

$$T(\mathbf{x} + \mathbf{y}) = T(\mathbf{x}) + T(\mathbf{y}), \qquad T(c\mathbf{x}) = c\,T(\mathbf{x}).$$
:::

::: {.theorem title="The standard matrix"}
Every linear map $T\colon \mathbb{R}^n \to \mathbb{R}^m$ is $T(\mathbf{x}) = A\mathbf{x}$
for exactly one $m \times n$ matrix $A$, namely

$$A = \begin{pmatrix} T(\mathbf{e}_1) & T(\mathbf{e}_2) & \cdots & T(\mathbf{e}_n) \end{pmatrix}.$$

> **[Added]** The columns of $A$ are where the unit vectors go. To find
> the matrix of a map, apply it to $\mathbf{e}_1, \dots, \mathbf{e}_n$ and
> write the results side by side.
:::

## 2.2 Rotations

::: {.example title="Rotation by $\theta$"}
Rotating the plane by an angle $\theta$ about the origin sends
$\mathbf{e}_1$ to $(\cos\theta, \sin\theta)^\top$ and $\mathbf{e}_2$ to
$(-\sin\theta, \cos\theta)^\top$, so its matrix is

$$R_\theta = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}.$$

> **[Unclear: page 2, line 7]** The sign in front of $\sin\theta$ in the
> top row looks like a "+". It must be "$-$" for $R_\theta\mathbf{e}_2$ to
> have length 1 and point to the left of $\mathbf{e}_1$, so it is typed
> as "$-$".
:::

![The unit square before and after a rotation by $\theta = 30^\circ$: the
columns of $R_\theta$ are the images of $\mathbf{e}_1$ and
$\mathbf{e}_2$.](figures/LA-L02-rotation.pdf){width=70%}

::: remark
A rotation keeps lengths and angles, so $\det R_\theta = \cos^2\theta + \sin^2\theta = 1$.
:::

In code, the same map is one matrix product:

```python
import numpy as np

theta = np.pi / 6
R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
R @ np.array([1.0, 0.0])  # where e1 goes
```

::: {.exercise title="Sheet 2, task 1"}
Find the standard matrix of the reflection in the line $y = x$.
:::
