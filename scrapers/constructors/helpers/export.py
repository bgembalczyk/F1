import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.results import ScrapeResult
from scrapers.constructors.complete_scraper import CompleteConstructorsDataExtractor


def constructor_name_initial(record: dict[str, Any]) -> str:
    # Try to get name from CurrentConstructorsListScraper /
    # FormerConstructorsListScraper
    constructor = record.get("constructor")
    if isinstance(constructor, dict):
        name = constructor.get("text") or ""
    elif isinstance(constructor, str):
        name = constructor
    else:
        # Try PrivateerTeamsListScraper
        name = record.get("team") or ""

    name = name.strip()
    if not name:
        return "other"

    match = re.search(r"[A-Za-z]", name)
    if not match:
        return "other"
    return match.group(0).upper()


def export_complete_constructors(
    *,
    output_dir: Path,
    include_urls: bool = True,
) -> None:
    options = init_scraper_options(None, include_urls=include_urls)
    scraper = CompleteConstructorsDataExtractor(options=options)
    data = scraper.fetch()
    scraper.logger.info("Pobrano rekordów: %s", len(data))

    output_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in data:
        grouped[constructor_name_initial(record)].append(record)

    for initial, records in grouped.items():
        filename = f"{initial}.json"
        json_path = output_dir / filename
        result = ScrapeResult(
            data=records,
            source_url=getattr(scraper, "url", None),
        )
        result.to_json(json_path, exporter=scraper.exporter)
