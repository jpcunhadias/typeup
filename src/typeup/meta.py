"""Header metadata for a note: course, label and date.

A note's header comes, in this order, from command-line flags, the note's
YAML front matter, and finally its path and file name (docs/metadata.md):

    LinearAlgebra/notes/2026-01-14 LA L01 Vectors.md
    -> course "Linear Algebra", label "LA L01", date "2026-01-14"
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, replace
from pathlib import Path

# Words kept lower case when a CamelCase folder name is split into words,
# except as the first word: "HistoryOfArt" -> "History of Art"
SMALL_WORDS = frozenset({"a", "an", "and", "at", "for", "in", "of", "on", "the", "to"})

_DATED = re.compile(r"^(\d{4}-\d{2}-\d{2})[ _]")
_CODE = re.compile(r"^[A-Z][A-Za-z]{1,3}$")
_NUMBERED = re.compile(r"^[A-Z][0-9]+$")


@dataclass(frozen=True)
class NoteMeta:
    """What the running header and the line under the title show."""

    course: str = ""
    label: str = ""
    date: str = ""  # YYYY-MM-DD, or free text printed as given

    def merged(self, override: NoteMeta) -> NoteMeta:
        """This metadata with every non-empty field of ``override`` on top."""
        return replace(
            self,
            course=override.course or self.course,
            label=override.label or self.label,
            date=override.date or self.date,
        )


def course_name(folder: str) -> str:
    """Turn a folder name into a course name: "LinearAlgebra" -> "Linear Algebra"."""
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", folder)
    words = re.split(r"[\s_-]+", spaced.strip())
    out = [w if i == 0 or w.lower() not in SMALL_WORDS else w.lower() for i, w in enumerate(words)]
    return " ".join(w for w in out if w)


def course_from_path(path: Path) -> str:
    """The course a note belongs to, from where it is stored.

    The folder directly under a ``courses/`` folder
    (``courses/LinearAlgebra/any/depth/x.md``), or else the folder above a
    ``notes/`` folder (``LinearAlgebra/notes/x.md``). Empty if neither
    applies.
    """
    parts = path.resolve().parent.parts
    for i, part in enumerate(parts[:-1]):
        if part.lower() == "courses":
            return course_name(parts[i + 1])
    for i in range(len(parts) - 1, 0, -1):
        if parts[i].lower() == "notes":
            return course_name(parts[i - 1])
    return ""


def date_and_label(stem: str) -> tuple[str, str]:
    """Date and label from a file name like ``2026-01-14 LA L01 Vectors``.

    Only a name that starts with a valid date gets a date; the word after it
    is the label if it looks like a course code (2-4 letters, capital first),
    followed by a number like ``L01``/``E03`` or by ``Sheet <n>``.
    """
    m = _DATED.match(stem)
    if not m:
        return "", ""
    date = m.group(1)
    try:
        dt.date.fromisoformat(date)
    except ValueError:
        return "", ""
    words = stem[11:].split()
    label = ""
    if words and _CODE.match(words[0]):
        if len(words) > 1 and _NUMBERED.match(words[1]):
            label = f"{words[0]} {words[1]}"
        elif len(words) > 2 and words[1] == "Sheet" and words[2].isdigit():
            label = f"{words[0]} Sheet {words[2]}"
        else:
            label = words[0]
    return date, label


def iso_date(text: str) -> str:
    """``text`` if it is a real YYYY-MM-DD date, else a ValueError."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ValueError(f"not a YYYY-MM-DD date: {text!r}")
    try:
        dt.date.fromisoformat(text)
    except ValueError:
        raise ValueError(f"not a date on the calendar: {text!r}") from None
    return text


def from_path(path: Path) -> NoteMeta:
    """Everything the path and file name say about a note."""
    date, label = date_and_label(path.stem)
    return NoteMeta(course=course_from_path(path), label=label, date=date)


def note_date(path: Path) -> str:
    """The YYYY-MM-DD date a note's file name starts with, or ""."""
    return date_and_label(path.stem)[0]
