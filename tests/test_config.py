from pathlib import Path

import pytest

from typeup.config import DEFAULT_FONT, load


def test_defaults_without_file(tmp_path: Path) -> None:
    cfg = load(tmp_path / "missing.toml")
    assert cfg.mainfont == DEFAULT_FONT
    assert cfg.mainfontoptions  # the default font is loaded by file name


def test_named_font_drops_file_options(tmp_path: Path) -> None:
    f = tmp_path / "config.toml"
    f.write_text('mainfont = "Helvetica Neue"\nfile_links = false\n')
    cfg = load(f)
    assert cfg.mainfont == "Helvetica Neue"
    assert cfg.mainfontoptions == []
    assert cfg.file_links is False


def test_unknown_key(tmp_path: Path) -> None:
    f = tmp_path / "config.toml"
    f.write_text("mainfnt = 'x'\n")
    with pytest.raises(ValueError, match="mainfnt"):
        load(f)


def test_env_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "c.toml"
    f.write_text('fontsize = "12pt"\n')
    monkeypatch.setenv("TYPEUP_CONFIG", str(f))
    assert load().fontsize == "12pt"


def test_legend_table(tmp_path: Path) -> None:
    f = tmp_path / "config.toml"
    f.write_text('[legend]\nadded = "by the tutor"\n')
    assert load(f).legend == {"added": "by the tutor"}
    f.write_text('[legend]\nadedd = "x"\n')
    with pytest.raises(ValueError, match="adedd"):
        load(f)
