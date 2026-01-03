from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from scrapers.base.composite_scraper import (
    CompositeScraper,
    CompositeScraperChildren,
)
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.drivers.single_scraper import SingleDriverScraper


class CompleteDriverScraper(CompositeScraper):
    url = F1DriversListScraper.CONFIG.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        self._html_adapter = options.with_source_adapter(policy=policy)
        self._policy = options.to_http_policy(options)
        super().__init__(options=options)

    def build_children(self) -> CompositeScraperChildren:
        list_scraper = F1DriversListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=self._policy,
                source_adapter=self._html_adapter,
            )
        )
        single_scraper = SingleDriverScraper(
            options=ScraperOptions(
                policy=self._policy,
                source_adapter=self._html_adapter,
            )
        )
        drivers_adapter = IterableSourceAdapter(list_scraper.fetch)

        return CompositeScraperChildren(
            list_scraper=list_scraper,
            single_scraper=single_scraper,
            records_adapter=drivers_adapter,
        )

    def get_detail_url(self, record: Dict[str, Any]) -> Optional[str]:
        driver_link = record.get("driver")
        if isinstance(driver_link, dict):
            return driver_link.get("url")
        return None

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    export_complete_drivers(
        output_dir=Path("../../data/wiki/drivers/complete_drivers"),
        include_urls=True,
    )
