import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.output_layout import output_targets
from scrapers.base.results import ScrapeResult
from scrapers.circuits.complete_scraper import F1CompleteCircuitDataExtractor


def circuit_name_initial(record: dict[str, Any]) -> str:
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
    output_dir: Path | None = None,
    include_urls: bool = True,
    legacy_output_enabled: bool = True,
    parser_version: str = "1.0.0",
    schema_version: str = "1.0.0",
) -> None:
    options = init_scraper_options(None, include_urls=include_urls)
    scraper = F1CompleteCircuitDataExtractor(options=options)
    data = scraper.fetch()
    scraper.logger.info("Pobrano rekordów: %s", len(data))

    output_dirs = [output_dir] if output_dir is not None else output_targets(
        category="circuits",
        layer="normalized",
        legacy_enabled=legacy_output_enabled,
    )
    for target_dir in output_dirs:
        target_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in data:
        grouped[circuit_name_initial(record)].append(record)

    for initial, records in grouped.items():
        filename = f"{initial}.json"
        for target_dir in output_dirs:
            json_path = target_dir / filename
            result = ScrapeResult(
                data=records,
                source_url=getattr(scraper, "url", None),
                parser_version=parser_version,
                schema_version=schema_version,
            )
            result.to_json(json_path, exporter=scraper.exporter, include_metadata=True)
