import re
from pathlib import Path
from typing import Any

from scrapers.base.export.export_helpers import export_grouped_json
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.parsers.helpers import extract_driver_text
from scrapers.drivers.complete_scraper import CompleteDriverDataExtractor


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
    scraper = CompleteDriverDataExtractor(options=options)
    data = scraper.fetch()
    export_grouped_json(scraper, data, output_dir, surname_initial)
