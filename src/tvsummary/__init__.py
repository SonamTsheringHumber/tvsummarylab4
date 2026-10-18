"""tvsummary: download TV shows from TVmaze and summarize them."""

from . import config
from .aggregations import (
    Aggregation,
    AverageRatingByLanguage,
    MissingValues,
    ShowsPerDecade,
    ShowsPerGenre,
    TopRatedShows,
    default_aggregations,
)
from .errors import DataShapeError, DownloadError, TVSummaryError
from .models import Show
from .report import build_summary, write_summary
from .sources import TVMazeSource

__all__ = [
    "Aggregation",
    "AverageRatingByLanguage",
    "DataShapeError",
    "DownloadError",
    "MissingValues",
    "Show",
    "ShowsPerDecade",
    "ShowsPerGenre",
    "TVMazeSource",
    "TVSummaryError",
    "TopRatedShows",
    "build_summary",
    "config",
    "default_aggregations",
    "write_summary",
]
