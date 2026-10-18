"""Entry point: wires the pieces together and prints messages."""

import logging
import sys

from tvsummary import (
    DownloadError,
    TVMazeSource,
    TVSummaryError,
    build_summary,
    config,
    default_aggregations,
    write_summary,
)
from tvsummary.logging_setup import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Download, summarize and save; exit with a message on failure."""
    configure_logging("INFO")
    logger.info("Starting a run")
    source = TVMazeSource()
    try:
        shows = source.fetch()
        if len(shows) < config.MIN_RECORDS:
            raise DownloadError(
                f"Only {len(shows)} usable records downloaded; "
                f"at least {config.MIN_RECORDS} are required."
            )
        summary = build_summary(shows, source.skipped_count, default_aggregations())
        write_summary(summary)
    except TVSummaryError as exc:
        logger.error("Run failed: %s", exc)
        sys.exit(f"Error: {exc}")
    except OSError as exc:
        logger.error("Could not write %s: %s", config.OUTPUT_PATH, exc)
        sys.exit(f"Error: could not write {config.OUTPUT_PATH}: {exc}")

    print(
        f"Processed {summary['records_processed']} shows "
        f"({source.skipped_count} skipped). Summary written to {config.OUTPUT_PATH}."
    )


if __name__ == "__main__":
    main()
