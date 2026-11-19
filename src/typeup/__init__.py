"""typeup: render typed-up study notes from Markdown to PDF.

The rendering itself is a pandoc Lua filter (``data/marks.lua``) and a LaTeX
header (``data/notes-header.tex``); this package finds them, works out each
note's header from its metadata or file name, and calls pandoc and XeLaTeX.
"""

from importlib.resources import files
from pathlib import Path

__version__ = "0.1.0"

PACKAGE_DIR = Path(str(files("typeup")))
DATA_DIR = PACKAGE_DIR / "data"
TEMPLATES_DIR = PACKAGE_DIR / "templates"
FILTER = DATA_DIR / "marks.lua"
HEADER = DATA_DIR / "notes-header.tex"
MPLSTYLE = PACKAGE_DIR / "notes.mplstyle"

__all__ = [
    "DATA_DIR",
    "FILTER",
    "HEADER",
    "MPLSTYLE",
    "PACKAGE_DIR",
    "TEMPLATES_DIR",
    "__version__",
]
