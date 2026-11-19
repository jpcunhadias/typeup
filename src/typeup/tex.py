"""Compile a .tex file with latexmk, aux files kept in build/ beside it."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ENGINES = {"pdf": "-pdf", "xe": "-xelatex", "lua": "-lualatex"}
_MAGIC = re.compile(r"^%\s*!TEX\s+(?:TS-)?program\s*=\s*(\S+)", re.IGNORECASE | re.MULTILINE)
_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


class CompileError(RuntimeError):
    pass


def _uses(source: str, package: str) -> bool:
    return (
        re.search(rf"^[^%\n]*\\usepackage(\[[^]]*\])?\{{[^}}]*{package}", source, re.M) is not None
    )


def pick_engine(source: str) -> str:
    """A ``% !TEX program = ...`` line wins; fontspec or unicode-math means
    XeLaTeX; otherwise pdfLaTeX."""
    if m := _MAGIC.search(source):
        magic = m.group(1).lower()
        for key, name in (("xe", "xelatex"), ("lua", "lualatex"), ("pdf", "pdflatex")):
            if magic == name:
                return key
    if _uses(source, "fontspec") or _uses(source, "unicode-math"):
        return "xe"
    return "pdf"


def first_errors(log: Path, limit: int = 30) -> str:
    """file:line:error lines, and the two lines TeX prints after each."""
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    pat = re.compile(r"^(\./|/)?[^:]+:\d+: |^! ")
    out: list[str] = []
    for i, line in enumerate(lines):
        if pat.match(line):
            out.extend(lines[i : i + 3])
        if len(out) >= limit:
            break
    return "\n".join(out[:limit])


def compile_tex(
    tex: Path, name: str = "", engine: str = "", png: bool = False, clean: bool = False
) -> Path | None:
    if not tex.is_file():
        raise CompileError(f"no such .tex file: {tex}")
    folder = tex.resolve().parent
    build = folder / "build"
    if clean:
        shutil.rmtree(build, ignore_errors=True)
        print(f"removed {build}")
        return None
    name = name.removesuffix(".pdf")
    if name and not _NAME.match(name):
        raise CompileError(f"--name may only contain letters, digits, . _ -: {name}")
    job = name or tex.stem
    source = tex.read_text(encoding="utf-8", errors="replace")
    engine = engine or pick_engine(source)
    if engine not in ENGINES:
        raise CompileError("--engine must be pdf, xe or lua")
    if shutil.which("latexmk") is None:
        raise CompileError("latexmk not found: install TeX Live (it includes latexmk)")
    flags = ["-interaction=nonstopmode", "-halt-on-error", "-file-line-error"]
    if _uses(source, "minted"):
        flags.append("-shell-escape")
    build.mkdir(exist_ok=True)
    cmd = ["latexmk", ENGINES[engine], f"-outdir={build}", f"-jobname={job}", *flags, tex.name]
    print(f":: {' '.join(cmd[:2] + flags)} -> {build}", file=sys.stderr)
    with (build / "latexmk.out").open("w", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, cwd=folder, stdout=fh, stderr=subprocess.STDOUT)
    log = build / f"{job}.log"
    if proc.returncode != 0:
        if log.is_file():
            detail = first_errors(log)
        else:
            tail = (build / "latexmk.out").read_text(encoding="utf-8", errors="replace")
            detail = "\n".join(tail.splitlines()[-20:])
        raise CompileError(f"compile failed. First errors from {log}:\n{detail}")
    pdf = folder / f"{job}.pdf"
    shutil.copyfile(build / f"{job}.pdf", pdf)
    if log.is_file():
        text = log.read_text(encoding="utf-8", errors="replace")
        n = len(re.findall(r"LaTeX Warning: (Reference|Citation).*undefined|Overfull \\hbox", text))
        if n:
            print(f"   {n} undefined-reference/citation or overfull-hbox warnings in {log}")
    if png:
        if shutil.which("pdftoppm") is None:
            raise CompileError("--png needs pdftoppm (poppler)")
        preview = build / "preview"
        preview.mkdir(exist_ok=True)
        for old in preview.glob(f"{job}-*.png"):
            old.unlink()
        subprocess.run(["pdftoppm", "-png", "-r", "80", str(pdf), str(preview / job)], check=True)
        print(f"   previews: {preview}/{job}-*.png")
    return pdf
