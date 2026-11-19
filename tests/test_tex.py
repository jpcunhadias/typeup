from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from typeup import TEMPLATES_DIR
from typeup.tex import CompileError, compile_tex, pick_engine


@pytest.mark.parametrize(
    ("source", "engine"),
    [
        ("% !TEX program = lualatex\n\\usepackage{fontspec}", "lua"),
        ("% !TeX TS-program = xelatex\n", "xe"),
        ("\\usepackage[no-math]{fontspec}\n", "xe"),
        ("\\usepackage{amsmath,unicode-math}\n", "xe"),
        ("% \\usepackage{fontspec}\n\\usepackage{amsmath}\n", "pdf"),
        ("\\documentclass{article}\n", "pdf"),
    ],
)
def test_pick_engine(source: str, engine: str) -> None:
    assert pick_engine(source) == engine


def test_bad_name(tmp_path: Path) -> None:
    tex = tmp_path / "a.tex"
    tex.write_text("x")
    with pytest.raises(CompileError, match="--name"):
        compile_tex(tex, name="has space")


@pytest.mark.tex
@pytest.mark.skipif(shutil.which("latexmk") is None, reason="latexmk not installed")
@pytest.mark.parametrize("template", ["homework", "cheatsheet"])
def test_templates_compile(tmp_path: Path, template: str) -> None:
    tex = tmp_path / f"{template}.tex"
    shutil.copyfile(TEMPLATES_DIR / f"{template}.tex", tex)
    pdf = compile_tex(tex, name=f"{template}-out")
    assert pdf is not None and pdf.read_bytes().startswith(b"%PDF")
