import re
from pathlib import Path
from typing import Any

from complete_extractor.complete_scraper_seasons import CompleteSeasonDataExtractor
from scrapers.options import ScraperOptions
from scrapers.results import ScrapeResult
from scrapers.services.result_export import ResultExportService


def season_filename(season_info: dict[str, Any]) -> str:
    year_text = season_info.get("text")
    if isinstance(year_text, str):
        year_text = year_text.strip()
        if year_text.isdigit():
            return f"{year_text}.json"
        slug = re.sub(r"[^\w]+", "_", year_text).strip("_").lower()
        if slug:
            return f"{slug}.json"
    return "unknown.json"


def export_complete_seasons(
    *,
    output_dir: Path,
    include_urls: bool = True,
) -> None:
    options = ScraperOptions(include_urls=include_urls)
    scraper = CompleteSeasonDataExtractor(options=options)
    data = scraper.fetch()
    scraper.logger.info("Pobrano rekordów: %s", len(data))

    output_dir.mkdir(parents=True, exist_ok=True)
    result_export_service = ResultExportService()

    for season_entry in data:
        season_info = season_entry.get("season")
        if not isinstance(season_info, dict):
            continue
        filename = season_filename(season_info)
        json_path = output_dir / filename
        result = ScrapeResult(
            data=[season_entry],
            source_url=getattr(scraper, "url", None),
        )
        result_export_service.to_json(result, json_path, exporter=scraper.exporter)
