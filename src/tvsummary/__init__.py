"""tvsummary: download TV shows from TVmaze and summarize them."""

from .aggregations import (
    Aggregation,
    AverageRatingByLanguage,
    MissingValues,
    ShowsPerDecade,
    ShowsPerGenre,
    TopRatedShows,
    default_aggregations,
)
from .config import Settings, load_settings
from .errors import (
    DataShapeError,
    DownloadError,
    OutputError,
    SettingsError,
    TVSummaryError,
)
from .models import Show
from .report import build_summary, pick_featured, write_json, write_summary
from .run_info import build_run_info
from .sources import TVMazeSource

__all__ = [
    "Aggregation",
    "AverageRatingByLanguage",
    "DataShapeError",
    "DownloadError",
    "MissingValues",
    "OutputError",
    "Settings",
    "SettingsError",
    "Show",
    "ShowsPerDecade",
    "ShowsPerGenre",
    "TVMazeSource",
    "TVSummaryError",
    "TopRatedShows",
    "build_run_info",
    "build_summary",
    "default_aggregations",
    "load_settings",
    "pick_featured",
    "write_json",
    "write_summary",
]
