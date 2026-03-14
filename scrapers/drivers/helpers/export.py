import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.parsers.helpers import extract_driver_text
from scrapers.base.results import ScrapeResult
from scrapers.drivers.complete_scraper import CompleteDriverScraper


def surname_initial(record: dict[str, Any]) -> str:
    driver_text = extract_driver_text(record)
    if not driver_text:
        return "other"

    parts = [part for part in driver_text.split() if part.strip()]
    if not parts:
        return "other"
    surname = parts[-1]
    match = re.search(r"[A-Za-z]", surname)
    if not match:
        return "other"
    return match.group(0).upper()


def export_complete_drivers(
    *,
    output_dir: Path,
    include_urls: bool = True,
) -> None:
    options = init_scraper_options(None, include_urls=include_urls)
    scraper = CompleteDriverScraper(options=options)
    data = scraper.fetch()
    scraper.logger.info("Pobrano rekordów: %s", len(data))

    output_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in data:
        grouped[surname_initial(record)].append(record)

    for initial, records in grouped.items():
        filename = f"{initial}.json"
        json_path = output_dir / filename
        result = ScrapeResult(
            data=records,
            source_url=getattr(scraper, "url", None),
        )
        result.to_json(json_path, exporter=scraper.exporter)
