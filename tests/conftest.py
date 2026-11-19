from __future__ import annotations

import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples" / "LinearAlgebra" / "notes"

needs_pandoc = pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
needs_xelatex = pytest.mark.skipif(
    shutil.which("xelatex") is None or shutil.which("pandoc") is None,
    reason="pandoc and XeLaTeX not installed",
)


@pytest.fixture(autouse=True)
def no_user_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests never read the developer's own ~/.config/typeup/config.toml."""
    monkeypatch.setenv("TYPEUP_CONFIG", str(tmp_path / "no-config.toml"))
