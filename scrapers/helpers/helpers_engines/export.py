from __future__ import annotations

from pathlib import Path
from typing import Any

from complete_extractor.complete_scraper_engines import F1CompleteEngineManufacturerDataExtractor
from scrapers.options import ScraperOptions
from scrapers.services.result_export import ResultExportService


def manufacturer_name_initial(record: dict[str, Any]) -> str:
    """Return the uppercased first letter of the manufacturer name, or 'other'."""
    manufacturer = record.get("manufacturer")
    if isinstance(manufacturer, dict):
        name = manufacturer.get("text", "") or ""
    elif isinstance(manufacturer, str):
        name = manufacturer
    else:
        name = ""
    initial = name.strip()[:1].upper()
    return initial if initial.isalpha() else "other"


def export_complete_engine_manufacturers(
    *,
    output_dir: Path,
    include_urls: bool = True,
) -> None:
    options = ScraperOptions(include_urls=include_urls)
    scraper = F1CompleteEngineManufacturerDataExtractor(options=options)
    data = scraper.fetch()
    result_export_service = ResultExportService()
    result_export_service.export_grouped_json(
        scraper,
        data,
        output_dir,
        key_fn=manufacturer_name_initial,
    )


__all__ = [
    "export_complete_engine_manufacturers",
    "manufacturer_name_initial",
]
