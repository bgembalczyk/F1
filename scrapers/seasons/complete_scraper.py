from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.ABC import F1Scraper
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper


class CompleteSeasonScraper(F1Scraper):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
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
            year = (
                int(year_text)
                if isinstance(year_text, str) and year_text.isdigit()
                else None
            )
            data = season_scraper.fetch_by_url(url, season_year=year)
            results.append(
                {
                    "season": season_info,
                    "tables": data[0] if data else {},
                },
            )

        return results


if __name__ == "__main__":
    from scrapers.seasons.helpers import export_complete_seasons

    export_complete_seasons(
        output_dir=Path("../../data/wiki/seasons/complete_seasons"),
        include_urls=True,
    )
