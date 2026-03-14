from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.composite_scraper import CompositeScraper
from scrapers.base.composite_scraper import CompositeScraperChildren
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.drivers.single_scraper import SingleDriverScraper


class CompleteDriverScraper(CompositeScraper):
    url = F1DriversListScraper.CONFIG.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = options or ScraperOptions()

        # Ten scraper zawsze potrzebuje URL-i (bo potem dociąga szczegóły)
        options.include_urls = True

        super().__init__(options=options)

    def build_children(self) -> CompositeScraperChildren:
        list_scraper = F1DriversListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=self.http_policy,
                source_adapter=self.source_adapter,
            ),
        )
        single_scraper = SingleDriverScraper(
            options=ScraperOptions(
                policy=self.http_policy,
                source_adapter=self.source_adapter,
            ),
        )
        drivers_adapter = IterableSourceAdapter(list_scraper.fetch)

        return CompositeScraperChildren(
            list_scraper=list_scraper,
            single_scraper=single_scraper,
            records_adapter=drivers_adapter,
        )

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
        driver_link = record.get("driver")
        if isinstance(driver_link, dict):
            return driver_link.get("url")
        return None

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    from scrapers.drivers.helpers.export import export_complete_drivers

    export_complete_drivers(
        output_dir=Path("../../data/wiki/drivers/complete_drivers"),
        include_urls=True,
    )
