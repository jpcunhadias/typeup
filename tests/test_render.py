"""End to end: the example notes render to PDF (needs pandoc and XeLaTeX)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from typeup.cli import main
from typeup.config import Config
from typeup.render import combine_notes, dated_notes, default_output, render_note

from .conftest import EXAMPLES, needs_pandoc, needs_xelatex


def test_dated_notes_range() -> None:
    all_notes = dated_notes(EXAMPLES)
    assert [n.name[:10] for n in all_notes] == ["2026-01-14", "2026-01-21"]
    assert len(dated_notes(EXAMPLES, until="2026-01-14")) == 1
    assert len(dated_notes(EXAMPLES, start="2026-01-15")) == 1


@pytest.mark.parametrize("bad", ["zzz", "2026-02-30"])
def test_combine_rejects_bad_range(bad: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as err:
        main(["combine", str(EXAMPLES), "-o", "x.pdf", "--from", bad])
    assert err.value.code == 2
    assert "--from" in capsys.readouterr().err
    with pytest.raises(ValueError):
        dated_notes(EXAMPLES, until=bad)


@needs_pandoc
@pytest.mark.parametrize(
    ("bounds", "count"),
    [
        ([], 2),
        (["--from", "2026-01-15"], 1),
        (["--until", "2026-01-14"], 1),
        (["--from", "2026-01-01", "--until", "2026-01-31"], 2),
    ],
)
def test_combine_cli_date_bounds_are_optional(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], bounds: list[str], count: int
) -> None:
    out = tmp_path / "all.tex"  # LaTeX output: no TeX run needed
    assert main(["combine", str(EXAMPLES), "-o", str(out), "--no-file-links", *bounds]) == 0
    assert f"({count} notes)" in capsys.readouterr().out


def test_default_output(tmp_path: Path) -> None:
    note = tmp_path / "a.md"
    assert default_output(note) == tmp_path / "a.pdf"
    (tmp_path / "pdf").mkdir()
    assert default_output(note) == tmp_path / "pdf" / "a.pdf"


def _copy_examples(tmp_path: Path) -> Path:
    dest = tmp_path / "LinearAlgebra" / "notes"
    shutil.copytree(EXAMPLES, dest, ignore=shutil.ignore_patterns("pdf"))
    return dest


@pytest.mark.tex
@needs_xelatex
def test_render_and_combine(tmp_path: Path) -> None:
    notes = _copy_examples(tmp_path)
    cfg = Config(file_links=False)
    for note in dated_notes(notes):
        pdf = render_note(note, cfg)
        assert pdf.read_bytes().startswith(b"%PDF")
    out, used = combine_notes(notes, tmp_path / "all.pdf", cfg)
    assert out.is_file() and len(used) == 2


@pytest.mark.tex
@needs_xelatex
def test_no_local_paths_in_pdf(tmp_path: Path) -> None:
    """With --no-file-links a note's PDF must not hold the local folder."""
    notes = _copy_examples(tmp_path)
    note = notes / "2026-01-14 LA L01 Vectors and spans.md"
    note.write_text(note.read_text() + "\nSee [the slides](../slides/week1.pdf).\n")
    out = tmp_path / "x.pdf"
    assert main(["render", "--no-file-links", str(note), "-o", str(out)]) == 0
    assert str(tmp_path).encode() not in out.read_bytes()


@needs_pandoc
def test_missing_note(tmp_path: Path) -> None:
    assert main(["render", str(tmp_path / "nope.md")]) == 1


def test_path_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["path", "filter"]) == 0
    assert capsys.readouterr().out.strip().endswith("marks.lua")


def test_template_command(tmp_path: Path) -> None:
    dest = tmp_path / "hw.tex"
    assert main(["template", "homework", str(dest)]) == 0
    assert "\\begin{problem}" in dest.read_text()
    assert main(["template", "homework", str(dest)]) == 1  # no overwrite


def _table_at_page_break(filler: int) -> str:
    """A section with a pipe table, pushed down the page by filler text."""
    para = "Filler text that wraps across the line so the page fills up at a steady pace, " * 2
    rows = "\n".join(
        f"| Dist{i} | $p(1-p)^{{k}}$ | {i} | {2 * i} "
        "| a longer cell that may wrap onto a second line |"
        for i in range(12)
    )
    head = "| Name | PMF | Mean | Var | Notes |\n|---|---|---|---|---|\n"
    return (
        "# Repro\n\n" + (para + "\n\n") * filler + "## The table section\n\n" + head + rows + "\n"
    )


@pytest.mark.tex
@needs_xelatex
@pytest.mark.parametrize("filler", [26, 41])
def test_table_head_not_repeated_above_heading(tmp_path: Path, filler: int) -> None:
    """A table starting near a page break must not leave a copy of its head
    at the top of the next page, above its own heading (these filler sizes
    showed it with the soft \\needspace)."""
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext not installed")
    note = tmp_path / "repro.md"
    note.write_text(_table_at_page_break(filler))
    out = tmp_path / "repro.pdf"
    assert main(["render", "--no-file-links", str(note), "-o", str(out)]) == 0
    text = subprocess.run(["pdftotext", str(out), "-"], capture_output=True, text=True).stdout
    lines = [line.strip() for line in text.splitlines()]
    assert lines.index("PMF") > lines.index("The table section")
