import logging

from tvsummary.logging_setup import configure_logging
from tvsummary.sources import TVMazeSource


def test_skipped_records_are_logged_as_warnings(caplog):
    source = TVMazeSource("https://example.invalid", 1)
    raw = [{"id": 1, "name": "A"}, {"id": 1, "name": "dup"}, {"name": "no id"}, "x"]
    with caplog.at_level(logging.WARNING, logger="tvsummary.sources"):
        source._to_shows(raw)
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 3
    assert "duplicate id 1" in caplog.text


def test_fetch_logs_how_many_shows_were_kept(monkeypatch, raw_records, caplog):
    monkeypatch.setattr(TVMazeSource, "_download", lambda self: raw_records)
    with caplog.at_level(logging.INFO, logger="tvsummary.sources"):
        TVMazeSource("https://example.invalid", 1).fetch()
    assert "Kept 4 shows and skipped 0" in caplog.text


def test_configure_logging_passes_the_level_on(monkeypatch):
    captured = {}
    monkeypatch.setattr(logging, "basicConfig", lambda **kw: captured.update(kw))
    configure_logging("DEBUG")
    assert captured["level"] == "DEBUG"
    assert "%(levelname)s" in captured["format"]
