"""The Lua filter, checked on pandoc's LaTeX output (no TeX needed)."""

from __future__ import annotations

import subprocess

import pytest

from typeup import FILTER

from .conftest import needs_pandoc

pytestmark = needs_pandoc


def to_latex(markdown: str, *extra: str) -> str:
    cmd = ["pandoc", "--from=markdown+bracketed_spans", "--to=latex", f"--lua-filter={FILTER}"]
    return subprocess.run(
        [*cmd, *extra], input=markdown, capture_output=True, text=True, check=True
    ).stdout


@pytest.mark.parametrize(
    ("label", "env"),
    [("Added", "markadded"), ("Your mark", "markyour"), ("Unclear", "markunclear")],
)
def test_mark_boxes(label: str, env: str) -> None:
    out = to_latex(f"> **[{label}]** text\n")
    assert f"\\begin{{{env}}}" in out
    assert f"\\end{{{env}}}" in out
    assert f"[{label}]" not in out


def test_unclear_with_place() -> None:
    out = to_latex("> **[Unclear: page 4, line 2]** Reads as $x_i$.\n")
    assert "\\emph{page 4, line 2}:" in out


def test_source_label_is_escaped() -> None:
    out = to_latex("> **[Board photo #3 & 4]** text\n")
    assert "\\begin{marksource}{Board photo \\#3 \\& 4}" in out


def test_several_marks_in_one_quote() -> None:
    out = to_latex("> **[Added]** one\n> **[Your mark]** two\n")
    assert out.index("markadded") < out.index("markyour")


def test_plain_quote_stays_a_quote() -> None:
    assert "\\begin{quote}" in to_latex("> just a quote\n")


def test_inline_unclear() -> None:
    assert "\\unclearinline{" in to_latex("the [$x_2$?]{.unclear} column\n")


def test_content_box_with_math_title() -> None:
    out = to_latex('::: {.theorem title="Weak duality for $c$"}\nBody.\n:::\n')
    assert "\\begin{nbtheorem}{Weak duality for \\(c\\)}" in out


def test_legend_and_proof() -> None:
    out = to_latex("::: legend\nx\n:::\n\n::: proof\ny\n:::\n")
    assert "\\begin{notelegend}" in out
    assert "\\begin{nbproof}{}" in out


def test_heading_kept_with_next() -> None:
    out = to_latex("# Title\n\ntext\n\n## Section\n\nmore text\n")
    before_section = out.split("\\subsection")[0]
    assert "\\needspace{" in before_section


def test_metadata_header() -> None:
    out = to_latex(
        "# T\n",
        "--metadata=course:Linear Algebra",
        "--metadata=label:LA L01",
        "--metadata=date:2026-01-14",
    )
    assert "\\renewcommand{\\notecourse}{Linear Algebra}" in out
    assert "\\renewcommand{\\notedate}{Wed 14 Jan 2026}" in out


def test_free_text_date_is_kept() -> None:
    out = to_latex("# T\n", "--metadata=date:Week 3")
    assert "\\renewcommand{\\notedate}{Week 3}" in out


def test_combine_marker() -> None:
    out = to_latex('::: {.typeup-note course="A & B" label="X L01" date="2026-01-21"}\n:::\n')
    assert "\\notebreak{A \\& B}{X L01}{Wed 21 Jan 2026}" in out


def test_file_links_stay_relative_without_notes_dir() -> None:
    out = to_latex("[the slides](../slides/week1.pdf)\n")
    assert "../slides/week1.pdf" in out


def test_legend_wording_from_metadata() -> None:
    out = to_latex("# T\n", "--metadata=legend-added:explained by the tutor")
    assert "\\renewcommand{\\addedrole}{explained by the tutor}" in out
