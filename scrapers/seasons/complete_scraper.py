from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup
from pathlib import Path

from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.runner import RunConfig
from scrapers.base.runner import run_and_export
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


if __name__ == "__main__":
    run_and_export(
        CompleteSeasonScraper,
        "seasons/f1_complete_seasons.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )