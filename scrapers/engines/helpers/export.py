import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.results import ScrapeResult
from scrapers.engines.complete_scraper import F1CompleteEngineManufacturerScraper


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
    scraper = F1CompleteEngineManufacturerScraper(options=options)
    data = scraper.fetch()
    scraper.logger.info("Pobrano rekordów: %s", len(data))

    output_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in data:
        grouped[manufacturer_name_initial(record)].append(record)

    for initial, records in grouped.items():
        filename = f"{initial}.json"
        json_path = output_dir / filename
        result = ScrapeResult(
            data=records,
            source_url=getattr(scraper, "url", None),
        )
        result.to_json(json_path, exporter=scraper.exporter)
