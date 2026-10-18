"""Building and writing the summary."""

import json
import logging
import random
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .aggregations import Aggregation
from .config import Settings
from .errors import OutputError
from .models import Show

logger = logging.getLogger(__name__)

SUMMARY_FILENAME = "summary.json"
RUN_INFO_FILENAME = "run_info.json"


def pick_featured(shows: list[Show], seed: int, sample_size: int) -> list[str]:
    """Choose sample_size show names at random; the same seed gives the same list.

    Names are sorted first so the result does not depend on download order.
    """
    names = sorted(show.name for show in shows)
    rng = random.Random(seed)
    return rng.sample(names, k=min(sample_size, len(names)))


def build_summary(
    shows: list[Show],
    skipped_count: int,
    aggregations: list[Aggregation],
    settings: Settings,
) -> dict[str, Any]:
    """Combine every aggregation into one dict ready to write as JSON.

    Calls compute() on each object without checking its subclass.
    """
    summary: dict[str, Any] = {
        "source_url": settings.source_url,
        "records_processed": len(shows),
        "records_skipped": skipped_count,
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    for aggregation in aggregations:
        summary[aggregation.name] = aggregation.compute(shows)
    summary["featured_shows"] = pick_featured(
        shows, settings.seed, settings.sample_size
    )
    logger.debug("Built a summary with %s keys", len(summary))
    return summary


def write_json(data: dict[str, Any], path: Path) -> None:
    """Write data to path as UTF-8 JSON with 2-space indent."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(data, indent=2, ensure_ascii=False)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise OutputError(f"Could not write {path}: {exc}") from exc
    logger.info("Wrote %s", path)


def write_summary(summary: dict[str, Any], path: Path) -> None:
    """Write the summary dict to path."""
    write_json(summary, path)
