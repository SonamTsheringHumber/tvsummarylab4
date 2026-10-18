"""The errors tvsummary raises on purpose. Only main() catches them."""


class TVSummaryError(Exception):
    """Base class for every failure the program expects."""


class DownloadError(TVSummaryError):
    """The records could not be downloaded."""


class DataShapeError(TVSummaryError):
    """The response did not have the shape the program expects."""


class SettingsError(TVSummaryError):
    """The settings file is missing, unreadable or incomplete."""


class OutputError(TVSummaryError):
    """The results could not be written to disk."""
