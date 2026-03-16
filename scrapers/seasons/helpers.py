import re
from pathlib import Path
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.output_layout import output_targets
from scrapers.base.results import ScrapeResult
from scrapers.seasons.complete_scraper import CompleteSeasonDataExtractor


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
    output_dir: Path | None = None,
    include_urls: bool = True,
    legacy_output_enabled: bool = True,
    parser_version: str = "1.0.0",
    schema_version: str = "1.0.0",
) -> None:
    options = init_scraper_options(None, include_urls=include_urls)
    scraper = CompleteSeasonDataExtractor(options=options)
    data = scraper.fetch()
    scraper.logger.info("Pobrano rekordów: %s", len(data))

    output_dirs = [output_dir] if output_dir is not None else output_targets(
        category="seasons",
        layer="normalized",
        legacy_enabled=legacy_output_enabled,
    )
    for target_dir in output_dirs:
        target_dir.mkdir(parents=True, exist_ok=True)

    for season_entry in data:
        season_info = season_entry.get("season")
        if not isinstance(season_info, dict):
            continue
        filename = season_filename(season_info)
        for target_dir in output_dirs:
            json_path = target_dir / filename
            result = ScrapeResult(
                data=[season_entry],
                source_url=getattr(scraper, "url", None),
                parser_version=parser_version,
                schema_version=schema_version,
            )
            result.to_json(json_path, exporter=scraper.exporter, include_metadata=True)
