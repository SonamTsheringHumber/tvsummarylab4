"""Entry point: python -m tvsummary.main [--config PATH]."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from .aggregations import default_aggregations
from .config import DEFAULT_CONFIG_PATH, Settings, load_settings
from .errors import DownloadError, TVSummaryError
from .logging_setup import configure_logging
from .report import (
    RUN_INFO_FILENAME,
    SUMMARY_FILENAME,
    build_summary,
    write_json,
    write_summary,
)
from .run_info import build_run_info
from .sources import TVMazeSource

logger = logging.getLogger(__name__)


def run(settings: Settings) -> dict[str, Any]:
    """Download, summarize and save. Raises a TVSummaryError on failure."""
    source = TVMazeSource(settings.source_url, settings.timeout)
    shows = source.fetch()
    if len(shows) < settings.min_records:
        raise DownloadError(
            f"Only {len(shows)} usable records downloaded; "
            f"at least {settings.min_records} are required."
        )
    summary = build_summary(
        shows, source.skipped_count, default_aggregations(settings.top_n), settings
    )
    write_summary(summary, settings.output_dir / SUMMARY_FILENAME)
    write_json(build_run_info(settings), settings.output_dir / RUN_INFO_FILENAME)
    return summary


def main(argv: list[str] | None = None) -> int:
    """Run the program. Return 0 on success and 1 on an expected failure."""
    parser = argparse.ArgumentParser(
        prog="tvsummary",
        description="Download TV shows from TVmaze and write a JSON summary.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="path to the TOML settings file (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    try:
        settings = load_settings(args.config)
        configure_logging(settings.log_level)
        logger.info("Starting a run with settings from %s", args.config)
        summary = run(settings)
    except TVSummaryError as exc:
        logger.error("Run failed: %s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Processed {summary['records_processed']} shows "
        f"({summary['records_skipped']} skipped). "
        f"Summary written to {settings.output_dir / SUMMARY_FILENAME}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
