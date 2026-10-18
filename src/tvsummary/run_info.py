"""Facts about a run, written next to the summary so it can be repeated."""

import platform
from dataclasses import asdict
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from .config import Settings


def tool_version(package: str) -> str:
    """Return the installed version of a package, or 'not installed'."""
    try:
        return version(package)
    except PackageNotFoundError:
        return "not installed"


def build_run_info(settings: Settings) -> dict[str, Any]:
    """Record the settings used, the Python version and the checking tools."""
    used = asdict(settings)
    used["output_dir"] = settings.output_dir.as_posix()
    return {
        "settings": used,
        "python": platform.python_version(),
        "tvsummary": tool_version("tvsummary"),
        "pytest": tool_version("pytest"),
        "mypy": tool_version("mypy"),
        "ruff": tool_version("ruff"),
    }
