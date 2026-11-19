from pathlib import Path

import pytest

from typeup.meta import (
    NoteMeta,
    course_from_path,
    course_name,
    date_and_label,
    from_path,
    strip_front_matter,
)


@pytest.mark.parametrize(
    ("folder", "name"),
    [
        ("OperationsResearch", "Operations Research"),
        ("HistoryOfArt", "History of Art"),
        ("LinearAlgebra", "Linear Algebra"),
        ("machine-learning", "machine learning"),
        ("Statistics", "Statistics"),
        ("TheoryOfComputation", "Theory of Computation"),
    ],
)
def test_course_name(folder: str, name: str) -> None:
    assert course_name(folder) == name


def test_course_from_notes_folder(tmp_path: Path) -> None:
    note = tmp_path / "LinearAlgebra" / "notes" / "x.md"
    assert course_from_path(note) == "Linear Algebra"


def test_course_from_courses_folder(tmp_path: Path) -> None:
    note = tmp_path / "courses" / "OperationsResearch" / "NOTATION.md"
    assert course_from_path(note) == "Operations Research"


def test_courses_folder_wins_over_notes(tmp_path: Path) -> None:
    note = tmp_path / "courses" / "HistoryOfArt" / "work" / "notes" / "x.md"
    assert course_from_path(note) == "History of Art"


def test_no_course(tmp_path: Path) -> None:
    assert course_from_path(tmp_path / "random" / "x.md") == ""


@pytest.mark.parametrize(
    ("stem", "expected"),
    [
        ("2026-01-14 LA L01 Vectors", ("2026-01-14", "LA L01")),
        ("2026-01-14 OR E03 Duality", ("2026-01-14", "OR E03")),
        ("2026-11-12 ML Sheet 6 clustering", ("2026-11-12", "ML Sheet 6")),
        ("2026-11-12 HoA quiz review", ("2026-11-12", "HoA")),
        ("2026-11-12_LA_L01", ("2026-11-12", "")),
        ("2026-11-12 lowercase words", ("2026-11-12", "")),
        ("2026-02-30 LA L01 bad date", ("", "")),
        ("NOTATION", ("", "")),
    ],
)
def test_date_and_label(stem: str, expected: tuple[str, str]) -> None:
    assert date_and_label(stem) == expected


def test_from_path(tmp_path: Path) -> None:
    note = tmp_path / "LinearAlgebra" / "notes" / "2026-01-14 LA L01 Vectors.md"
    assert from_path(note) == NoteMeta("Linear Algebra", "LA L01", "2026-01-14")


def test_merged_keeps_empty_fields() -> None:
    base = NoteMeta("A", "B", "2026-01-01")
    assert base.merged(NoteMeta(label="X")) == NoteMeta("A", "X", "2026-01-01")


def test_strip_front_matter() -> None:
    text = "---\ncourse: X\n---\n# Title\n\n---\n\nrule above\n"
    assert strip_front_matter(text) == "# Title\n\n---\n\nrule above\n"
    assert strip_front_matter("# No front matter\n") == "# No front matter\n"
