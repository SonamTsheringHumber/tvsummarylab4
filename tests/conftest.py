from pathlib import Path
from typing import Any

import pytest

from tvsummary.config import Settings, load_settings
from tvsummary.models import Show


@pytest.fixture
def raw_records() -> list[dict[str, Any]]:
    """Four hand-made API records with known gaps."""
    return [
        {
            "id": 1,
            "name": "Alpha",
            "genres": ["Drama", "Crime"],
            "language": "English",
            "premiered": "1995-03-02",
            "rating": {"average": 8.0},
            "network": {"name": "Net"},
        },
        {
            "id": 2,
            "name": "Beta",
            "genres": ["Drama"],
            "language": "English",
            "premiered": "2004-01-01",
            "rating": {"average": 6.0},
            "webChannel": {"name": "Web"},
        },
        {
            "id": 3,
            "name": "Gamma",
            "genres": [],
            "language": "Japanese",
            "premiered": None,
            "rating": {"average": None},
            "network": None,
        },
        {
            "id": 4,
            "name": "Delta",
            "genres": ["Comedy"],
            "language": None,
            "premiered": "2012-06-01",
            "rating": {"average": 9.0},
        },
    ]


@pytest.fixture
def shows(raw_records: list[dict[str, Any]]) -> list[Show]:
    return [Show(raw) for raw in raw_records]


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """A valid settings file that writes into tmp_path."""
    path = tmp_path / "tvsummary.toml"
    path.write_text(
        'source_url = "https://example.invalid/shows"\n'
        "timeout = 1\n"
        f'output_dir = "{(tmp_path / "out").as_posix()}"\n'
        "seed = 7\n"
        "sample_size = 2\n"
        'log_level = "DEBUG"\n'
        "min_records = 2\n"
        "top_n = 2\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def settings(config_file: Path) -> Settings:
    return load_settings(config_file)
