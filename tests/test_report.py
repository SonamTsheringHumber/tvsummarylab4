import json

import pytest

from tvsummary.aggregations import default_aggregations
from tvsummary.errors import OutputError
from tvsummary.models import Show
from tvsummary.report import build_summary, pick_featured, write_summary
from tvsummary.run_info import build_run_info


@pytest.fixture
def many_shows() -> list[Show]:
    return [Show({"id": i, "name": f"Show {i:02d}"}) for i in range(30)]


def test_same_seed_gives_same_featured_list(many_shows):
    first = pick_featured(many_shows, seed=42, sample_size=5)
    second = pick_featured(many_shows, seed=42, sample_size=5)
    assert first == second
    assert len(first) == 5


def test_featured_list_does_not_depend_on_download_order(many_shows):
    forward = pick_featured(many_shows, seed=42, sample_size=5)
    backward = pick_featured(list(reversed(many_shows)), seed=42, sample_size=5)
    assert forward == backward


def test_different_seeds_give_different_lists(many_shows):
    assert pick_featured(many_shows, 1, 5) != pick_featured(many_shows, 2, 5)


def test_sample_size_larger_than_data_returns_every_name(many_shows):
    result = pick_featured(many_shows, seed=1, sample_size=100)
    assert sorted(result) == sorted(show.name for show in many_shows)


def test_summary_keeps_lab_03_keys_and_adds_featured_shows(shows, settings):
    summary = build_summary(shows, 3, default_aggregations(2), settings)
    assert list(summary) == [
        "source_url",
        "records_processed",
        "records_skipped",
        "generated_at_utc",
        "shows_per_genre",
        "average_rating_by_language",
        "shows_per_decade",
        "top_rated_shows",
        "missing_values",
        "featured_shows",
    ]
    assert summary["records_processed"] == 4
    assert summary["records_skipped"] == 3
    assert len(summary["top_rated_shows"]) == 2
    assert len(summary["featured_shows"]) == 2


def test_write_summary_creates_folders_and_valid_json(tmp_path):
    target = tmp_path / "a" / "b" / "summary.json"
    write_summary({"name": "Café"}, target)
    assert json.loads(target.read_text(encoding="utf-8")) == {"name": "Café"}


def test_write_failure_raises_output_error(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file, not a folder", encoding="utf-8")
    with pytest.raises(OutputError, match="Could not write"):
        write_summary({"a": 1}, blocker / "summary.json")


def test_run_info_records_settings_and_versions(settings):
    info = build_run_info(settings)
    assert info["settings"]["seed"] == 7
    assert info["settings"]["output_dir"].endswith("out")
    assert {"python", "pytest", "mypy", "ruff"} <= set(info)
    json.dumps(info)
