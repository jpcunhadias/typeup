"""The ``typeup`` command."""

from __future__ import annotations

import argparse
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path

from . import FILTER, HEADER, MPLSTYLE, TEMPLATES_DIR, __version__
from .config import load
from .meta import NoteMeta
from .render import RenderError, combine_notes, render_note
from .tex import CompileError, compile_tex

TEMPLATES = sorted(p.stem for p in TEMPLATES_DIR.glob("*.tex"))
PATHS = {"filter": FILTER, "header": HEADER, "mplstyle": MPLSTYLE, "templates": TEMPLATES_DIR}


def _meta_flags(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("header (overrides front matter and the file name)")
    g.add_argument("--course", default="", help='course name, e.g. "Linear Algebra"')
    g.add_argument("--label", default="", help='short label, e.g. "LA L01"')
    g.add_argument("--date", default="", help="YYYY-MM-DD, or any text to print as is")


def _render_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--no-file-links",
        action="store_true",
        help="keep links to local files relative instead of absolute (no local paths in the PDF)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="typeup", description="Render typed-up study notes from Markdown to PDF."
    )
    parser.add_argument("--version", action="version", version=f"typeup {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("render", help="one PDF per note")
    p.add_argument("notes", nargs="+", type=Path, metavar="NOTE.md")
    p.add_argument("-o", "--out", type=Path, help="output PDF (one note only)")
    _meta_flags(p)
    _render_flags(p)

    p = sub.add_parser("combine", help="all dated notes of a folder in one PDF")
    p.add_argument("folder", type=Path, metavar="DIR")
    p.add_argument("-o", "--out", type=Path, required=True, help="output PDF")
    p.add_argument("--from", dest="start", default="", metavar="YYYY-MM-DD")
    p.add_argument("--until", default="", metavar="YYYY-MM-DD")
    p.add_argument("--title", default="", help="title page (default: Notes: <course>)")
    _meta_flags(p)
    _render_flags(p)

    p = sub.add_parser("tex", help="compile a .tex file with latexmk")
    p.add_argument("tex", type=Path, metavar="FILE.tex")
    p.add_argument("--name", default="", help="output file name, without .pdf")
    p.add_argument("--engine", choices=["pdf", "xe", "lua"], default="")
    p.add_argument("--png", action="store_true", help="page previews in build/preview/")
    p.add_argument("--clean", action="store_true", help="remove build/")

    p = sub.add_parser("template", help="copy a LaTeX template")
    p.add_argument("name", choices=TEMPLATES)
    p.add_argument("dest", type=Path, nargs="?", help="where to write it (default: stdout)")

    p = sub.add_parser("path", help="print where a bundled file is (for plain pandoc use)")
    p.add_argument("what", choices=sorted(PATHS))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command in ("render", "combine"):
            cfg = load()
            if args.no_file_links:
                cfg.file_links = False
            flags = NoteMeta(course=args.course, label=args.label, date=args.date)
            if args.command == "render":
                if args.out and len(args.notes) > 1:
                    print("typeup: --out works with one note only", file=sys.stderr)
                    return 2
                for note in args.notes:
                    print(f"ok: {render_note(note, cfg, args.out, flags)}")
            else:
                out, notes = combine_notes(
                    args.folder, args.out, cfg, args.start, args.until, args.title, flags
                )
                print(f"ok: {out} ({len(notes)} notes)")
        elif args.command == "tex":
            pdf = compile_tex(args.tex, args.name, args.engine, args.png, args.clean)
            if pdf:
                print(f"ok: {pdf}")
        elif args.command == "template":
            src = TEMPLATES_DIR / f"{args.name}.tex"
            if args.dest is None:
                sys.stdout.write(src.read_text(encoding="utf-8"))
            elif args.dest.exists():
                print(f"typeup: {args.dest} exists, not overwriting it", file=sys.stderr)
                return 1
            else:
                shutil.copyfile(src, args.dest)
                print(f"ok: {args.dest}")
        elif args.command == "path":
            print(PATHS[args.what])
    except (RenderError, CompileError, ValueError) as err:
        print(f"typeup: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
