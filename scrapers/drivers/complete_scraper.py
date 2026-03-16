from pathlib import Path
from typing import Any

from scrapers.base.complete_extractor_base import CompleteExtractorBase
from scrapers.base.options import ScraperOptions
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.drivers.single_scraper import SingleDriverScraper


class CompleteDriverDataExtractor(CompleteExtractorBase):
    url = F1DriversListScraper.CONFIG.url

    def build_list_scraper(self, options: ScraperOptions) -> F1DriversListScraper:
        return F1DriversListScraper(options=self.list_scraper_options(options))

    def build_single_scraper(self, options: ScraperOptions) -> SingleDriverScraper:
        return SingleDriverScraper(options=self.single_scraper_options(options))

    def extract_detail_url(self, record: dict[str, Any]) -> str | None:
        driver_link = record.get("driver")
        if isinstance(driver_link, dict):
            return driver_link.get("url")
        return None


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import build_cli_main
    from scrapers.base.run_config import RunConfig
    from scrapers.drivers.helpers.export import export_complete_drivers

    build_cli_main(
        target=lambda: export_complete_drivers(
            output_dir=Path("../../data/wiki/drivers/complete_drivers"),
            include_urls=True,
        ),
        base_config=RunConfig(),
        profile="complete_extractor",
    )()
