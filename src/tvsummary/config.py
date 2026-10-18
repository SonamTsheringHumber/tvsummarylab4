"""Settings for the tvsummary package, read from a TOML file."""

import logging
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import SettingsError

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("config/tvsummary.toml")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


@dataclass(frozen=True)
class Settings:
    """Every setting the program reads. Frozen so a run cannot change them."""

    source_url: str
    timeout: float
    output_dir: Path
    seed: int
    sample_size: int
    log_level: str
    min_records: int
    top_n: int


def _read_toml(path: Path) -> dict[str, Any]:
    """Parse the TOML file, turning low-level errors into SettingsError."""
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError as exc:
        raise SettingsError(f"Settings file not found: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise SettingsError(f"Settings file is not valid TOML: {path}: {exc}") from exc
    except OSError as exc:
        raise SettingsError(f"Settings file could not be read: {path}: {exc}") from exc


def _check(settings: Settings, path: Path) -> None:
    """Reject values that parse but make no sense."""
    problems: list[str] = []
    if settings.log_level not in LOG_LEVELS:
        problems.append(f"log_level must be one of {', '.join(LOG_LEVELS)}")
    if settings.timeout <= 0:
        problems.append("timeout must be greater than 0")
    if settings.sample_size < 0:
        problems.append("sample_size must not be negative")
    if settings.min_records < 0:
        problems.append("min_records must not be negative")
    if settings.top_n < 1:
        problems.append("top_n must be at least 1")
    if problems:
        raise SettingsError(f"Settings file {path} is invalid: {'; '.join(problems)}.")


def load_settings(path: Path) -> Settings:
    """Read the TOML file at path into a frozen Settings object."""
    data = _read_toml(path)
    try:
        settings = Settings(
            source_url=str(data["source_url"]),
            timeout=float(data["timeout"]),
            output_dir=Path(str(data["output_dir"])),
            seed=int(data["seed"]),
            sample_size=int(data["sample_size"]),
            log_level=str(data["log_level"]).upper(),
            min_records=int(data["min_records"]),
            top_n=int(data["top_n"]),
        )
    except KeyError as exc:
        raise SettingsError(
            f"Settings file {path} is missing the setting {exc.args[0]!r}."
        ) from exc
    except (TypeError, ValueError) as exc:
        raise SettingsError(f"Settings file {path} has a bad value: {exc}") from exc
    _check(settings, path)
    logger.debug("Loaded settings from %s", path)
    return settings
