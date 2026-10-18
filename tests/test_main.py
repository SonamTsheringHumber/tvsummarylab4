import json
import logging

import requests

from tvsummary import sources
from tvsummary.errors import DownloadError
from tvsummary.main import main
from tvsummary.sources import TVMazeSource


def patch_download(monkeypatch, records):
    monkeypatch.setattr(TVMazeSource, "_download", lambda self: records)


def test_successful_run_returns_zero_and_writes_both_files(
    monkeypatch, config_file, raw_records, capsys, tmp_path
):
    patch_download(monkeypatch, raw_records)
    assert main(["--config", str(config_file)]) == 0

    out = capsys.readouterr().out
    assert "Processed 4 shows (0 skipped)" in out
    summary = json.loads((tmp_path / "out" / "summary.json").read_text("utf-8"))
    info = json.loads((tmp_path / "out" / "run_info.json").read_text("utf-8"))
    assert len(summary["featured_shows"]) == 2
    assert info["settings"]["seed"] == 7


def test_same_seed_gives_same_featured_shows_across_runs(
    monkeypatch, config_file, raw_records, tmp_path
):
    patch_download(monkeypatch, raw_records)
    summary_path = tmp_path / "out" / "summary.json"
    featured = []
    for _ in range(2):
        assert main(["--config", str(config_file)]) == 0
        summary = json.loads(summary_path.read_text("utf-8"))
        featured.append(summary["featured_shows"])
    assert featured[0] == featured[1]


def test_missing_config_returns_one_with_a_single_error_line(tmp_path, capsys):
    assert main(["--config", str(tmp_path / "missing.toml")]) == 1
    captured = capsys.readouterr()
    error_lines = [ln for ln in captured.err.splitlines() if ln.startswith("Error:")]
    assert len(error_lines) == 1
    assert "not found" in error_lines[0]
    assert "Traceback" not in captured.err
    assert captured.out == ""


def test_failed_download_returns_one_and_prints_message(
    monkeypatch, config_file, capsys
):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(sources.requests, "get", fake_get)
    assert main(["--config", str(config_file)]) == 1
    err = capsys.readouterr().err
    assert "Error: Could not connect" in err
    assert "Traceback" not in err


def test_too_few_records_returns_one(monkeypatch, config_file, raw_records, capsys):
    patch_download(monkeypatch, raw_records[:1])
    assert main(["--config", str(config_file)]) == 1
    assert "at least 2 are required" in capsys.readouterr().err


def test_failure_is_logged_at_error_level(monkeypatch, config_file, caplog):
    def boom(self):
        raise DownloadError("boom")

    monkeypatch.setattr(TVMazeSource, "_download", boom)
    with caplog.at_level(logging.DEBUG):
        assert main(["--config", str(config_file)]) == 1
    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(errors) == 1
    assert "boom" in errors[0].getMessage()


def test_successful_run_logs_milestones(monkeypatch, config_file, raw_records, caplog):
    patch_download(monkeypatch, raw_records)
    with caplog.at_level(logging.DEBUG):
        assert main(["--config", str(config_file)]) == 0
    messages = [r.getMessage() for r in caplog.records]
    assert any(m.startswith("Kept 4 shows") for m in messages)
    assert any(m.startswith("Wrote ") for m in messages)
