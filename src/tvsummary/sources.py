"""Getting the data. The only module that imports requests."""

import logging
from typing import Any

import requests

from . import config
from .errors import DataShapeError, DownloadError
from .models import Show

logger = logging.getLogger(__name__)


class TVMazeSource:
    """Downloads shows from the TVmaze API and returns Show objects."""

    def __init__(
        self,
        url: str = config.SOURCE_URL,
        timeout: float = config.TIMEOUT_SECONDS,
    ) -> None:
        self.url = url
        self.timeout = timeout
        self.skipped_count = 0

    def _download(self) -> list[Any]:
        """Download the raw JSON list, raising a TVSummaryError on any problem."""
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            raise DownloadError(
                f"The request to {self.url} timed out after {self.timeout} seconds."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise DownloadError(
                f"Could not connect to {self.url}. Check your internet connection."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise DownloadError(f"The server returned an error: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise DownloadError(f"The request to {self.url} failed: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise DataShapeError(
                f"The response from {self.url} was not valid JSON."
            ) from exc

        if not isinstance(data, list):
            raise DataShapeError(
                "Unexpected response format: expected a list of shows."
            )
        logger.debug("Downloaded %s raw records", len(data))
        return data

    def _to_shows(self, raw_records: list[Any]) -> list[Show]:
        """Keep usable records (dict, has id, no duplicate id) as Show objects."""
        seen_ids: set[Any] = set()
        shows: list[Show] = []
        for position, item in enumerate(raw_records):
            if not isinstance(item, dict):
                logger.warning("Skipping record %s: not a JSON object", position)
                continue
            show_id = item.get("id")
            if show_id is None:
                logger.warning("Skipping record %s: it has no id", position)
                continue
            if show_id in seen_ids:
                logger.warning("Skipping record %s: duplicate id %s", position, show_id)
                continue
            seen_ids.add(show_id)
            shows.append(Show(item))
        self.skipped_count = len(raw_records) - len(shows)
        return shows

    def fetch(self) -> list[Show]:
        """Download and return a list of Show objects."""
        shows = self._to_shows(self._download())
        logger.info("Kept %s shows and skipped %s", len(shows), self.skipped_count)
        return shows
