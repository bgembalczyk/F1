import re
from pathlib import Path
from typing import Any

from scrapers.base.helpers.helpers import init_scraper_options
from scrapers.base.services.result_export_service import ResultExportService
from scrapers.engines.complete_scraper_engines import F1CompleteEngineManufacturerDataExtractor


def manufacturer_name_initial(record: dict[str, Any]) -> str:
    manufacturer = record.get("manufacturer")
    if isinstance(manufacturer, dict):
        name = manufacturer.get("text") or ""
    elif isinstance(manufacturer, str):
        name = manufacturer
    else:
        name = ""

    if not name:
        return "other"

    match = re.search(r"[A-Za-z]", name)
    if not match:
        return "other"
    return match.group(0).upper()


def export_complete_engine_manufacturers(
    *,
    output_dir: Path,
    include_urls: bool = True,
) -> None:
    options = init_scraper_options(None, include_urls=include_urls)
    scraper = F1CompleteEngineManufacturerDataExtractor(options=options)
    data = scraper.fetch()

    result_export_service = ResultExportService()
    result_export_service.export_grouped_json(
        scraper,
        data,
        output_dir,
        manufacturer_name_initial,
    )
