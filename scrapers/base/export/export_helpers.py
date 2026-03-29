from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

from scrapers.base.export.exporters import DataExporter
from scrapers.base.results import ScrapeResult
from validation.validator_base import ExportRecord


def export_grouped_json(
    scraper: Any,
    data: list[dict[str, Any]],
    output_dir: Path,
    key_fn: Callable[[dict[str, Any]], str],
) -> None:
    scraper.logger.info("Pobrano rekordów: %s", len(data))
    output_dir.mkdir(parents=True, exist_ok=True)
    exporter = getattr(scraper, "exporter", None) or DataExporter()

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in data:
        key = key_fn(record).strip()
        grouped[key if key else "other"].append(record)

    for key, records in grouped.items():
        result = ScrapeResult(
            data=records,
            source_url=getattr(scraper, "url", None),
        )
        exporter.to_json(result, output_dir / f"{key}.json")


def fieldnames_from_union(data: list[ExportRecord]) -> list[str]:
    keys: list[str] = []
    for row in data:
        for key in row:
            if key not in keys:
                keys.append(key)
    return keys


def fieldnames_from_first_row(data: list[ExportRecord]) -> list[str]:
    return list(data[0].keys()) if data else []
