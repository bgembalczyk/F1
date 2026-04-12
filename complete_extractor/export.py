import re
from pathlib import Path
from typing import Any

from complete_extractor.circuits_complete_scraper import F1CompleteCircuitDataExtractor
from complete_extractor.complete_scraper_drivers import CompleteDriverDataExtractor
from complete_extractor.complete_scraper_engines import F1CompleteEngineManufacturerDataExtractor
from complete_extractor.constructors_complete_scraper import CompleteConstructorsDataExtractor
from infrastructure.helpers import init_scraper_options
from scrapers.parsers.helpers import extract_driver_text
from scrapers.services.result_export import ResultExportService


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
    ResultExportService().export_grouped_json(
        scraper,
        data,
        output_dir,
        constructor_name_initial,
    )


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
    ResultExportService().export_grouped_json(
        scraper,
        data,
        output_dir,
        surname_initial,
    )
