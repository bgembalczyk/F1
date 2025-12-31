from __future__ import annotations

import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from pathlib import Path

from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.results import ScrapeResult
from scrapers.base.scraper import F1Scraper
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper


class CompleteSeasonScraper(F1Scraper):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        options = init_scraper_options(options, include_urls=True)
        options.with_fetcher()
        super().__init__(options=options)
        self.url = SeasonsListScraper.CONFIG.url
        self._options = options

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        list_scraper = SeasonsListScraper(options=self._options)
        seasons = list_scraper.parse(soup)

        results: List[Dict[str, Any]] = []
        season_scraper = SingleSeasonScraper(options=self._options)

        for season in seasons:
            season_info = season.get("season")
            if not isinstance(season_info, dict):
                continue
            url = season_info.get("url")
            if not isinstance(url, str) or not url:
                continue
            year_text = season_info.get("text")
            year = int(year_text) if isinstance(year_text, str) and year_text.isdigit() else None
            data = season_scraper.fetch_by_url(url, season_year=year)
            results.append(
                {
                    "season": season_info,
                    "tables": data[0] if data else {},
                }
            )

        return results


def _season_filename(season_info: Dict[str, Any]) -> str:
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
    options = init_scraper_options(None, include_urls=include_urls)
    scraper = CompleteSeasonScraper(options=options)
    data = scraper.fetch()
    scraper.logger.info("Pobrano rekordów: %s", len(data))

    output_dir.mkdir(parents=True, exist_ok=True)

    for season_entry in data:
        season_info = season_entry.get("season")
        if not isinstance(season_info, dict):
            continue
        filename = _season_filename(season_info)
        json_path = output_dir / filename
        result = ScrapeResult(
            data=[season_entry],
            source_url=getattr(scraper, "url", None),
        )
        result.to_json(json_path, exporter=scraper.exporter)


if __name__ == "__main__":
    export_complete_seasons(
        output_dir=Path("../../data/wiki/complete_seasons"),
        include_urls=True,
    )
