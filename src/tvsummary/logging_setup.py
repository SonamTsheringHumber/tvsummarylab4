"""Logging configuration. Called once, from main()."""

import logging


def configure_logging(level="INFO"):
    """Send log records to standard error at the given level."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
