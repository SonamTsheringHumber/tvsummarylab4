"""Entry point: wires the pieces together and prints messages."""

import logging
import sys

from tvsummary import (
    DownloadError,
    TVMazeSource,
    TVSummaryError,
    build_run_info,
    build_summary,
    default_aggregations,
    load_settings,
    write_json,
    write_summary,
)
from tvsummary.config import DEFAULT_CONFIG_PATH
from tvsummary.logging_setup import configure_logging
from tvsummary.report import RUN_INFO_FILENAME, SUMMARY_FILENAME

logger = logging.getLogger(__name__)


def main() -> None:
    """Download, summarize and save; exit with a message on failure."""
    try:
        settings = load_settings(DEFAULT_CONFIG_PATH)
        configure_logging(settings.log_level)
        logger.info("Starting a run")
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
    except TVSummaryError as exc:
        logger.error("Run failed: %s", exc)
        sys.exit(f"Error: {exc}")

    print(
        f"Processed {summary['records_processed']} shows "
        f"({summary['records_skipped']} skipped). "
        f"Summary written to {settings.output_dir / SUMMARY_FILENAME}."
    )


if __name__ == "__main__":
    main()
