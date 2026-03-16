from pathlib import Path
from typing import Any

from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper


class CompleteSeasonDataExtractor(CompositeDataExtractor):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        self._options = options
        super().__init__(options=options)
        self.url = SeasonsListScraper.CONFIG.url

    def build_children(self) -> CompositeDataExtractorChildren:
        list_scraper = SeasonsListScraper(options=self._options)
        return CompositeDataExtractorChildren(
            list_scraper=list_scraper,
            single_scraper=SingleSeasonScraper(options=self._options),
            records_adapter=IterableSourceAdapter(list_scraper.fetch),
        )

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
        season_info = record.get("season")
        if not isinstance(season_info, dict):
            return None
        url = season_info.get("url")
        return url if isinstance(url, str) and url else None

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        season_info = record.get("season")
        if not isinstance(season_info, dict):
            return {
                "season": {},
                "tables": details or {},
            }
        return {
            "season": season_info,
            "tables": details or {},
        }


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import run_cli_entrypoint
    from scrapers.base.run_config import RunConfig
    from scrapers.seasons.helpers import export_complete_seasons

    run_cli_entrypoint(
        target=lambda: export_complete_seasons(
            output_dir=Path("../../data/wiki/seasons/complete_seasons"),
            include_urls=True,
        ),
        base_config=RunConfig(),
    )
