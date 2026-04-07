import re
from pathlib import Path
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.services.result_export_service import ResultExportService
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
    output_dir: Path,
    include_urls: bool = True,
) -> None:
    options = init_scraper_options(None, include_urls=include_urls)
    scraper = F1CompleteCircuitDataExtractor(options=options)
    data = scraper.fetch()

    result_export_service = ResultExportService()
    result_export_service.export_grouped_json(
        scraper,
        data,
        output_dir,
        circuit_name_initial,
    )
