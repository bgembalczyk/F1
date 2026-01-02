from __future__ import annotations

import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup
from pathlib import Path

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.results import ScrapeResult
from scrapers.base.scraper import F1Scraper
from scrapers.seasons.helpers import export_complete_seasons
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
            if data and isinstance(data[0], dict):
                entries = data[0].get("entries")
                if isinstance(entries, list):
                    data[0]["entries"] = season_scraper._merge_entries_drivers(entries)
            results.append(
                {
                    "season": season_info,
                    "tables": data[0] if data else {},
                }
            )

        return results


if __name__ == "__main__":
    export_complete_seasons(
        output_dir=Path("../../data/wiki/seasons/complete_seasons"),
        include_urls=True,
    )
