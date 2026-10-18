from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from tvsummary.config import load_settings
from tvsummary.errors import SettingsError

KEYS = [
    "source_url",
    "timeout",
    "output_dir",
    "seed",
    "sample_size",
    "log_level",
    "min_records",
    "top_n",
]


def test_valid_file_loads(config_file):
    settings = load_settings(config_file)
    assert settings.seed == 7
    assert settings.sample_size == 2
    assert settings.timeout == 1.0
    assert settings.output_dir.name == "out"


def test_settings_are_frozen(settings):
    with pytest.raises(FrozenInstanceError):
        settings.seed = 99


def test_missing_file_raises_settings_error(tmp_path):
    with pytest.raises(SettingsError, match="not found"):
        load_settings(tmp_path / "nope.toml")


def test_invalid_toml_raises_settings_error(tmp_path):
    path = tmp_path / "bad.toml"
    path.write_text("this is = = not toml", encoding="utf-8")
    with pytest.raises(SettingsError, match="not valid TOML"):
        load_settings(path)


@pytest.mark.parametrize("key", KEYS)
def test_missing_setting_raises_settings_error(config_file: Path, key: str):
    lines = config_file.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if not line.startswith(f"{key} =")]
    config_file.write_text("\n".join(kept), encoding="utf-8")
    with pytest.raises(SettingsError, match=f"missing the setting '{key}'"):
        load_settings(config_file)


def test_unknown_log_level_raises_settings_error(config_file: Path):
    text = config_file.read_text(encoding="utf-8").replace("DEBUG", "LOUD")
    config_file.write_text(text, encoding="utf-8")
    with pytest.raises(SettingsError, match="log_level"):
        load_settings(config_file)
