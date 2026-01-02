import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.results import ScrapeResult
from scrapers.base.scraper import F1Scraper
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.drivers.single_scraper import SingleDriverScraper


class CompleteDriverScraper(F1Scraper):
    url = F1DriversListScraper.CONFIG.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        html_adapter = options.with_source_adapter()
        policy = options.to_http_policy()
        super().__init__(options=options)

        self.list_scraper = F1DriversListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=policy,
                source_adapter=html_adapter,
            )
        )
        self.single_scraper = SingleDriverScraper(
            options=ScraperOptions(
                policy=policy,
                source_adapter=html_adapter,
            )
        )
        self.drivers_adapter = IterableSourceAdapter(self.list_scraper.fetch)

    def fetch(self) -> List[Dict[str, Any]]:
        drivers = self.drivers_adapter.get()
        complete: List[Dict[str, Any]] = []

        for driver in drivers:
            if not isinstance(driver, dict):
                raise TypeError(
                    "F1DriversListScraper musi zwracać dict, "
                    f"otrzymano: {type(driver).__name__}"
                )

            record = dict(driver)
            driver_url: Optional[str] = None
            driver_link = record.get("driver")
            if isinstance(driver_link, dict):
                driver_url = driver_link.get("url")

            details: Optional[Dict[str, Any]] = None
            if driver_url:
                details_list = self.single_scraper.fetch_by_url(driver_url)
                if details_list:
                    details = details_list[0]

            record["details"] = details
            complete.append(record)

        self._data = complete
        return self._data

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    export_complete_drivers(
        output_dir=Path("../../data/wiki/drivers/complete_drivers"),
        include_urls=True,
    )
