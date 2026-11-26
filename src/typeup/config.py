"""User defaults for the PDF look, from a TOML file.

Looked up at ``$TYPEUP_CONFIG``, else ``$XDG_CONFIG_HOME/typeup/config.toml``
(``~/.config/typeup/config.toml``). Every key is optional::

    mainfont = "Helvetica Neue"   # a font installed on your system
    mainfontoptions = []          # fontspec options for it
    fontsize = "11pt"
    margin = "3cm"
    linestretch = 1.25
    file_links = true             # see docs/syntax.md, "Links to files"

    [legend]                      # what each mark means, in the legend
    added = "explained by the tutor"
"""

from __future__ import annotations

import math
import os
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

# TeX Gyre Heros ships with TeX Live, so the default works everywhere; it is
# loaded by file name, so it needs no system font installation
DEFAULT_FONT = "texgyreheros"
DEFAULT_FONT_OPTIONS = (
    "Extension=.otf",
    "UprightFont=*-regular",
    "BoldFont=*-bold",
    "ItalicFont=*-italic",
    "BoldItalicFont=*-bolditalic",
)

LEGEND_KEYS = ("added", "your", "unclear", "source")


@dataclass
class Config:
    mainfont: str = DEFAULT_FONT
    mainfontoptions: list[str] = field(default_factory=lambda: list(DEFAULT_FONT_OPTIONS))
    fontsize: str = "11pt"
    margin: str = "3cm"
    linestretch: float = 1.25
    file_links: bool = True
    legend: dict[str, str] = field(default_factory=dict)


def config_path() -> Path:
    if env := os.environ.get("TYPEUP_CONFIG"):
        return Path(env).expanduser()
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "typeup" / "config.toml"


def _check_types(path: Path, data: dict[str, Any]) -> None:
    """A ValueError naming the file and key for any value of the wrong type."""

    def fail(key: str, want: str) -> None:
        raise ValueError(f"{path}: {key} must be {want}, not {data[key]!r}")

    for key in ("mainfont", "fontsize", "margin"):
        if key in data and not (isinstance(data[key], str) and data[key].strip()):
            fail(key, "a non-empty string")
    opts = data.get("mainfontoptions", [])
    if not (isinstance(opts, list) and all(isinstance(o, str) for o in opts)):
        fail("mainfontoptions", 'a list of strings, like ["Scale=0.95"]')
    stretch = data.get("linestretch", 1)
    number = isinstance(stretch, int | float) and not isinstance(stretch, bool)
    if not (number and math.isfinite(stretch) and stretch > 0):
        fail("linestretch", "a finite positive number")
    if not isinstance(data.get("file_links", True), bool):
        fail("file_links", "true or false (no quotes)")
    legend = data.get("legend", {})
    if not isinstance(legend, dict):
        fail("legend", f"a [legend] table with keys {', '.join(LEGEND_KEYS)}")
    bad = sorted(set(legend) - set(LEGEND_KEYS))
    if bad:
        raise ValueError(f"{path}: unknown [legend] key(s): {', '.join(bad)}")
    for key, value in legend.items():
        if not isinstance(value, str):
            raise ValueError(f"{path}: legend.{key} must be a string, not {value!r}")


def load(path: Path | None = None) -> Config:
    """The config file's values on top of the defaults."""
    path = path or config_path()
    cfg = Config()
    if not path.is_file():
        return cfg
    try:
        data: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        raise ValueError(f"{path}: not valid TOML: {err}") from err
    known = {f.name for f in fields(Config)}
    unknown = sorted(set(data) - known)
    if unknown:
        raise ValueError(f"{path}: unknown key(s): {', '.join(unknown)}")
    _check_types(path, data)
    if "mainfont" in data and "mainfontoptions" not in data:
        # a font given by name needs none of the default font's file options
        cfg.mainfontoptions = []
    for key, value in data.items():
        setattr(cfg, key, value)
    return cfg
