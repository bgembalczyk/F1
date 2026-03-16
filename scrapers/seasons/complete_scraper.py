from typing import Any

from tqdm import tqdm

from scrapers.base.data_extractor import BaseDataExtractor
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.output_layout import output_dir_for
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper


class CompleteSeasonDataExtractor(BaseDataExtractor):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self.url = SeasonsListScraper.CONFIG.url
        self._options = options

    def fetch(self) -> list[dict[str, Any]]:
        list_scraper = SeasonsListScraper(options=self._options)
        seasons = list_scraper.fetch()

        results: list[dict[str, Any]] = []
        season_scraper = SingleSeasonScraper(options=self._options)

        for season in tqdm(seasons, desc="CompleteSeasonDataExtractor", unit="season"):
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

        self._data = results
        return self._data


if __name__ == "__main__":
    from scrapers.seasons.helpers import export_complete_seasons

    export_complete_seasons(
        output_dir=output_dir_for(category="seasons", layer="normalized"),
        include_urls=True,
    )
