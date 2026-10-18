"""The errors tvsummary raises on purpose. Only main() catches them."""


class TVSummaryError(Exception):
    """Base class for every failure the program expects."""


class DownloadError(TVSummaryError):
    """The records could not be downloaded."""


class DataShapeError(TVSummaryError):
    """The response did not have the shape the program expects."""
