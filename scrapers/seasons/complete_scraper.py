from pathlib import Path
from typing import Any

from scrapers.base.complete_extractor_base import CompleteExtractorBase
from scrapers.base.options import ScraperOptions
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper


class CompleteSeasonDataExtractor(CompleteExtractorBase):
    url = SeasonsListScraper.CONFIG.url

    def build_list_scraper(self, options: ScraperOptions) -> SeasonsListScraper:
        return SeasonsListScraper(options=self.list_scraper_options(options))

    def build_single_scraper(self, options: ScraperOptions) -> SingleSeasonScraper:
        return SingleSeasonScraper(options=self.single_scraper_options(options))

    def extract_detail_url(self, record: dict[str, Any]) -> str | None:
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
    from scrapers.base.cli_entrypoint import build_cli_main
    from scrapers.base.run_config import RunConfig
    from scrapers.seasons.helpers import export_complete_seasons

    build_cli_main(
        target=lambda: export_complete_seasons(
            output_dir=Path("../../data/wiki/seasons/complete_seasons"),
            include_urls=True,
        ),
        base_config=RunConfig(),
        profile="complete_extractor",
    )()
