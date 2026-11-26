"""Markdown notes to PDF with pandoc + XeLaTeX, one note or several."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from . import COMBINE_FILTER, FILTER, HEADER
from .config import Config
from .meta import NoteMeta, from_path, iso_date, note_date

MIN_PANDOC = (3, 0)


class RenderError(RuntimeError):
    """pandoc or LaTeX failed; the message says why."""


def pandoc_version(pandoc: str = "pandoc") -> tuple[int, ...]:
    exe = shutil.which(pandoc)
    if exe is None:
        raise RenderError("pandoc not found: install pandoc 3 or newer (https://pandoc.org)")
    out = subprocess.run([exe, "--version"], capture_output=True, text=True, check=True).stdout
    m = re.match(r"pandoc(?:\.exe)? (\d+(?:\.\d+)*)", out)
    if not m:
        raise RenderError(f"cannot read the pandoc version from: {out.splitlines()[0]}")
    version = tuple(int(x) for x in m.group(1).split("."))
    if version < MIN_PANDOC:
        raise RenderError(f"pandoc {m.group(1)} is too old: typeup needs 3.0 or newer")
    return version


def common_args(cfg: Config) -> list[str]:
    args = [
        "--from=markdown+bracketed_spans",
        "--pdf-engine=xelatex",
        f"--include-in-header={HEADER}",
        f"--lua-filter={FILTER}",
        f"--variable=mainfont:{cfg.mainfont}",
        f"--variable=fontsize:{cfg.fontsize}",
        f"--variable=geometry:margin={cfg.margin}",
        f"--variable=linestretch:{cfg.linestretch}",
        "--variable=colorlinks:true",
        "--variable=linkcolor:addedframe",
        "--variable=urlcolor:addedframe",
        "--variable=filecolor:addedframe",
        # xcolor's table option, for the striped table rows (notes-header.tex)
        "--variable=classoption:table",
    ]
    args += [f"--variable=mainfontoptions:{opt}" for opt in cfg.mainfontoptions]
    return args


def meta_args(meta: NoteMeta) -> list[str]:
    """-M flags: they override the note's front matter."""
    return [f"--metadata={k}:{v}" for k, v in vars(meta).items() if v]


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def defaults_file(folder: Path, cfg: Config, meta: NoteMeta) -> Path:
    """Metadata that a note's own front matter overrides: the header values
    from its path and the config's legend wording, as a YAML file."""
    values = {k: v for k, v in vars(meta).items() if v}
    values |= {f"legend-{k}": v for k, v in cfg.legend.items()}
    path = folder / "defaults.yaml"
    path.write_text("".join(f"{k}: {_quote(v)}\n" for k, v in values.items()), encoding="utf-8")
    return path


def run_pandoc(args: Sequence[str], notes_dir: Path | None, cfg: Config) -> None:
    """Run pandoc; on success print only its own warnings (missing glyphs too)."""
    env = dict(os.environ)
    env.pop("TYPEUP_NOTES_DIR", None)
    if cfg.file_links and notes_dir is not None:
        env["TYPEUP_NOTES_DIR"] = str(notes_dir.resolve())
    proc = subprocess.run(["pandoc", *args], capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        # a filter's own error (a bad date, say) without the Lua traceback
        for line in proc.stderr.splitlines():
            if line.startswith("typeup: "):
                raise RenderError(line.removeprefix("typeup: "))
        raise RenderError(proc.stderr.strip() or f"pandoc exited with {proc.returncode}")
    for line in proc.stderr.splitlines():
        if "WARNING" in line or "Missing character" in line:
            print(line, file=sys.stderr)


def default_output(note: Path) -> Path:
    """``pdf/<name>.pdf`` beside the note if that folder exists, else beside it."""
    pdf_dir = note.parent / "pdf"
    return (pdf_dir if pdf_dir.is_dir() else note.parent) / f"{note.stem}.pdf"


def render_note(
    note: Path, cfg: Config, out: Path | None = None, flags: NoteMeta | None = None
) -> Path:
    """Render one note. The header comes from ``flags``, then the note's front
    matter, then its path (the path's values go in as a metadata file, which
    front matter overrides)."""
    if not note.is_file():
        raise RenderError(f"no such note: {note}")
    pandoc_version()
    out = out or default_output(note)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        derived = defaults_file(Path(tmp), cfg, from_path(note))
        args = [
            str(note),
            *common_args(cfg),
            f"--metadata-file={derived}",
            *meta_args(flags or NoteMeta()),
            f"--resource-path={note.parent}",
            f"--output={out}",
        ]
        run_pandoc(args, note.parent, cfg)
    return out


_META_TEMPLATE = "$course$\x1f$label$\x1f$date$\n"


def front_matter_meta(note: Path) -> NoteMeta:
    """course / label / date as set in the note's own front matter."""
    with tempfile.TemporaryDirectory() as tmp:
        tpl = Path(tmp) / "meta.plain"
        tpl.write_text(_META_TEMPLATE, encoding="utf-8")
        proc = subprocess.run(
            ["pandoc", str(note), "--to=plain", f"--template={tpl}"],
            capture_output=True,
            text=True,
            check=False,
        )
    if proc.returncode != 0:
        raise RenderError(proc.stderr.strip())
    course, label, date = (proc.stdout.rstrip("\n").split("\x1f") + ["", "", ""])[:3]
    return NoteMeta(course=course.strip(), label=label.strip(), date=date.strip())


def dated_notes(folder: Path, start: str = "", until: str = "") -> list[Path]:
    """The notes in ``folder`` whose names start with a date in the range."""
    for bound in (start, until):
        if bound:
            iso_date(bound)
    notes = []
    for f in sorted(folder.glob("*.md")):
        d = note_date(f)
        if d and (not start or d >= start) and (not until or d <= until):
            notes.append(f)
    return notes


def combine_notes(
    folder: Path,
    out: Path,
    cfg: Config,
    start: str = "",
    until: str = "",
    title: str = "",
    flags: NoteMeta | None = None,
) -> tuple[Path, list[Path]]:
    """All dated notes in a folder, in date order, in one PDF with a contents
    page; each note starts on a new page with its own header."""
    if not folder.is_dir():
        raise RenderError(f"no such folder: {folder}")
    pandoc_version()
    notes = dated_notes(folder, start, until)
    if not notes:
        raise RenderError(
            f"no dated notes in {folder} between {start or 'the start'} and {until or 'the end'}"
        )
    parts = []
    for note in notes:
        meta = from_path(note).merged(front_matter_meta(note)).merged(flags or NoteMeta())
        attrs = " ".join(f"{k}={_quote(v)}" for k, v in vars(meta).items() if v)
        # combine.lua reads the note on its own (so its references, footnotes
        # and legend wording stay its own) and puts it after the marker;
        # marks.lua turns the marker into \notebreak: a new page, numbering
        # restarted and this note's header
        src = _quote(str(note.resolve()))
        parts.append(f"::: {{.typeup-note src={src} {attrs}}}\n:::\n\n")
    span = f"{note_date(notes[0])} to {note_date(notes[-1])}"
    if not title:
        course = from_path(notes[0]).course
        title = f"Notes: {course}" if course else "Notes"
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        combined = Path(tmp) / "combined.md"
        combined.write_text("".join(parts), encoding="utf-8")
        args = [
            str(combined),
            f"--lua-filter={COMBINE_FILTER}",
            *common_args(cfg),
            f"--metadata-file={defaults_file(Path(tmp), cfg, NoteMeta())}",
            "--toc",
            "--toc-depth=1",
            f"--resource-path={folder}",
            f"--metadata=title:{title}",
            f"--metadata=date:{span}",
            f"--output={out}",
        ]
        run_pandoc(args, folder, cfg)
    return out, notes
