from typing import Any

import pytest
import requests

from tvsummary import sources
from tvsummary.errors import DataShapeError, DownloadError
from tvsummary.sources import TVMazeSource

URL = "https://example.invalid/shows"


class FakeResponse:
    """Stands in for requests.Response so no network is needed."""

    def __init__(self, payload: Any = None, error: Exception | None = None) -> None:
        self.payload = payload
        self.error = error

    def raise_for_status(self) -> None:
        if self.error is not None:
            raise self.error

    def json(self) -> Any:
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def make_get(response: FakeResponse):
    return lambda *args, **kwargs: response


def test_connection_failure_raises_download_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(sources.requests, "get", fake_get)
    with pytest.raises(DownloadError, match="connect") as info:
        TVMazeSource(URL, 1).fetch()
    assert isinstance(info.value.__cause__, requests.ConnectionError)


def test_timeout_raises_download_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.Timeout("slow")

    monkeypatch.setattr(sources.requests, "get", fake_get)
    with pytest.raises(DownloadError, match="timed out"):
        TVMazeSource(URL, 1).fetch()


def test_http_error_raises_download_error(monkeypatch):
    response = FakeResponse(error=requests.HTTPError("500 Server Error"))
    monkeypatch.setattr(sources.requests, "get", make_get(response))
    with pytest.raises(DownloadError, match="server returned"):
        TVMazeSource(URL, 1).fetch()


def test_invalid_json_raises_data_shape_error(monkeypatch):
    response = FakeResponse(payload=ValueError("bad json"))
    monkeypatch.setattr(sources.requests, "get", make_get(response))
    with pytest.raises(DataShapeError, match="valid JSON"):
        TVMazeSource(URL, 1).fetch()


def test_non_list_response_raises_data_shape_error(monkeypatch):
    response = FakeResponse(payload={"not": "a list"})
    monkeypatch.setattr(sources.requests, "get", make_get(response))
    with pytest.raises(DataShapeError, match="list of shows"):
        TVMazeSource(URL, 1).fetch()


def test_fetch_turns_records_into_shows(monkeypatch, raw_records):
    response = FakeResponse(payload=raw_records)
    monkeypatch.setattr(sources.requests, "get", make_get(response))
    source = TVMazeSource(URL, 1)
    shows = source.fetch()
    assert [show.name for show in shows] == ["Alpha", "Beta", "Gamma", "Delta"]
    assert source.skipped_count == 0


def test_unusable_records_are_skipped_and_counted():
    source = TVMazeSource(URL, 1)
    raw = [{"id": 1, "name": "A"}, {"id": 1, "name": "dup"}, {"name": "no id"}, "x"]
    shows = source._to_shows(raw)
    assert [show.name for show in shows] == ["A"]
    assert source.skipped_count == 3
