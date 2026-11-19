# Linear Algebra, lecture of 14 Jan: vectors, linear combinations, span

Typed on 15 Jan 2026 from the handwritten note of 14 Jan (6 pages) and the
board photos.

::: legend
> **[Added]** A linear combination is a weighted sum of vectors …
> **[Your mark]** "?" next to the definition of span.
> **[Unclear: page 3, line 4]** Reads as $c_1 = 2$ or $c_1 = 3$.
> **[From the board, photo 4]** The picture of two arrows in the plane.

Plain text is what was written in the lecture, tidied.
:::

## What this lecture is about

Which vectors can be built from a given set of vectors by scaling and
adding them. That question comes back in every later topic: solving
$A\mathbf{x} = \mathbf{b}$ asks whether $\mathbf{b}$ can be built from the
columns of $A$.

## Where to learn it

| Source | Pages | What is there |
|---|---|---|
| Course textbook, ch. 1 | pp. 1–14 | vectors in $\mathbb{R}^n$, linear combinations |
| Course textbook, ch. 1 | pp. 15–22 | span, worked examples |
| Lecture slides, week 1 | slides 4–19 | the same, with pictures |

Used in: Exercise sheet 1, tasks 2 and 3.

## 1.1 Vectors in $\mathbb{R}^n$

A vector in $\mathbb{R}^n$ is an ordered list of $n$ real numbers, written
as a column:

$$\mathbf{v} = \begin{pmatrix} v_1 \\ \vdots \\ v_n \end{pmatrix}.$$

Vectors are added entry by entry, and multiplied by a scalar $c$ entry by
entry: $(c\mathbf{v})_i = c\, v_i$.

> **[Added]** "Scalar" here just means a real number. The word is used to
> tell numbers apart from vectors.

## 1.2 Linear combinations

::: {.definition title="Linear combination"}
Given vectors $\mathbf{v}_1, \dots, \mathbf{v}_k \in \mathbb{R}^n$ and
scalars $c_1, \dots, c_k$, the vector

$$c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + \dots + c_k\mathbf{v}_k$$

is a *linear combination* of $\mathbf{v}_1, \dots, \mathbf{v}_k$ with
weights $c_1, \dots, c_k$.

> **[Added]** A linear combination is a weighted sum of vectors. The
> weights may be zero or negative.
:::

::: {.example title="Two vectors in the plane"}
Let $\mathbf{u} = (1, 2)^\top$ and $\mathbf{w} = (3, 1)^\top$. Then

$$2\mathbf{u} - \mathbf{w} = \begin{pmatrix} 2 - 3 \\ 4 - 1 \end{pmatrix} = \begin{pmatrix} -1 \\ 3 \end{pmatrix}.$$

> **[Unclear: page 3, line 4]** Reads as $c_1 = 2$ or $c_1 = 3$. The
> result $(-1, 3)^\top$ only works with $c_1 = 2$, so that is what is
> typed here.
> **[From the board, photo 4]** The picture of two arrows in the plane,
> with $2\mathbf{u}$ drawn tip to tail with $-\mathbf{w}$.
:::

## 1.3 Span

::: {.definition title="Span"}
The *span* of $\mathbf{v}_1, \dots, \mathbf{v}_k$, written
$\operatorname{span}\{\mathbf{v}_1, \dots, \mathbf{v}_k\}$, is the set of
all their linear combinations.

> **[Your mark]** "?" next to the definition of span.
:::

::: {.theorem title="Span of two vectors in the plane"}
If $\mathbf{u}, \mathbf{w} \in \mathbb{R}^2$ are not multiples of each
other, then $\operatorname{span}\{\mathbf{u}, \mathbf{w}\} = \mathbb{R}^2$.
:::

::: proof
For any $\mathbf{b} \in \mathbb{R}^2$ the system
$c_1\mathbf{u} + c_2\mathbf{w} = \mathbf{b}$ has two equations and two
unknowns, and its determinant $u_1 w_2 - u_2 w_1$ is not zero, since
$\mathbf{u}$ and $\mathbf{w}$ are not multiples of each other. So it has a
solution.
:::

The pivot of the first column is [$u_1$?]{.unclear} in the lecturer's
notation.

::: {.exercise title="Sheet 1, task 2"}
Decide whether $(5, 5)^\top$ is in the span of $\mathbf{u}$ and
$\mathbf{w}$ from Example 2, and if so give the weights.
:::
