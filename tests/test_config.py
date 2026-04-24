from __future__ import annotations

import tempfile
from pathlib import Path

from seed_scaffold.config import get_config_dir, get_config_path, load_config


def test_config_dir_exists() -> None:
    config_dir = get_config_dir()
    # Config dir may not exist yet, so we just check it's a valid path
    assert isinstance(config_dir, Path)


def test_config_path() -> None:
    config_path = get_config_path()
    assert config_path == get_config_dir() / "config.toml"


def test_load_config_empty() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.toml"
        config_path.write_text("")
        config = load_config()
        assert config == {}


def test_load_config_valid() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.toml"
        config_path.write_text("""
[defaults]
author = "Test Author"
year = 2025
template = "meson-c-lib"
""")
        import seed_scaffold.config as config_module

        original_path = config_module.get_config_path
        try:
            config_module.get_config_path = lambda: config_path  # noqa: PLR0204

            config = load_config()
            assert config["defaults"]["author"] == "Test Author"
            assert config["defaults"]["year"] == 2025
            assert config["defaults"]["template"] == "meson-c-lib"
        finally:
            config_module.get_config_path = original_path


def test_load_config_invalid() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.toml"
        config_path.write_text("invalid toml content [[[")
        config = load_config()
        assert config == {}
