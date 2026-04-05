import re
from pathlib import Path
from typing import Any

from scrapers.base.export.export_helpers import export_grouped_json
from scrapers.base.helpers.http import init_scraper_options
from scrapers.constructors.complete_scraper import CompleteConstructorsDataExtractor


def constructor_name_initial(record: dict[str, Any]) -> str:
    constructor = record.get("constructor")
    if isinstance(constructor, dict):
        name = constructor.get("text") or ""
        if not name:
            names = constructor.get("names")
            if isinstance(names, list) and names:
                first_name = names[0]
                if isinstance(first_name, str):
                    name = first_name
    elif isinstance(constructor, str):
        name = constructor
    else:
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
    export_grouped_json(scraper, data, output_dir, constructor_name_initial)
