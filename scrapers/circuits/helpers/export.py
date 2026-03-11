import re
from collections import defaultdict
from pathlib import Path
from typing import Any
from typing import Dict

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.results import ScrapeResult
from scrapers.circuits.complete_scraper import F1CompleteCircuitScraper


def circuit_name_initial(record: Dict[str, Any]) -> str:
    name_data = record.get("name") or {}
    name_list = name_data.get("list") or []
    if not name_list:
        return "other"

    main_name = name_list[0] if isinstance(name_list[0], str) else ""
    if not main_name:
        return "other"

    match = re.search(r"[A-Za-z]", main_name)
    if not match:
        return "other"
    return match.group(0).upper()


def export_complete_circuits(
        *,
        output_dir: Path,
        include_urls: bool = True,
) -> None:
    options = init_scraper_options(None, include_urls=include_urls)
    scraper = F1CompleteCircuitScraper(options=options)
    data = scraper.fetch()
    scraper.logger.info("Pobrano rekordów: %s", len(data))

    output_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[Dict[str, Any]]] = defaultdict(list)
    for record in data:
        grouped[circuit_name_initial(record)].append(record)

    for initial, records in grouped.items():
        filename = f"{initial}.json"
        json_path = output_dir / filename
        result = ScrapeResult(
            data=records,
            source_url=getattr(scraper, "url", None),
        )
        result.to_json(json_path, exporter=scraper.exporter)
