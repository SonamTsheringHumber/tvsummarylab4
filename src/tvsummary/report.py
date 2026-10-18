"""Building and writing the summary."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import config
from .aggregations import Aggregation
from .models import Show

logger = logging.getLogger(__name__)


def build_summary(
    shows: list[Show],
    skipped_count: int,
    aggregations: list[Aggregation],
    url: str = config.SOURCE_URL,
) -> dict[str, Any]:
    """Combine every aggregation into one dict ready to write as JSON.

    Calls compute() on each object without checking its subclass.
    """
    summary: dict[str, Any] = {
        "source_url": url,
        "records_processed": len(shows),
        "records_skipped": skipped_count,
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    for aggregation in aggregations:
        summary[aggregation.name] = aggregation.compute(shows)
    logger.debug("Built a summary with %s keys", len(summary))
    return summary


def write_summary(
    summary: dict[str, Any], path: str | Path = config.OUTPUT_PATH
) -> None:
    """Write the summary dict to path as UTF-8 JSON with 2-space indent."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(summary, indent=2, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")
    logger.info("Wrote %s", path)
