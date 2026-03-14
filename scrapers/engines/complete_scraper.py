from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.composite_scraper import CompositeScraper
from scrapers.base.composite_scraper import CompositeScraperChildren
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.engines.single_scraper import SingleEngineManufacturerScraper


class F1CompleteEngineManufacturerScraper(CompositeScraper):
    """
    Pobiera listę producentów silników z dwóch źródeł (główna lista oraz lista
    'Indianapolis 500 only'), a następnie zaciąga wszystkie infoboksy i tabele
    z artykułu każdego producenta.
    """

    url = EngineManufacturersListScraper.CONFIG.url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.include_urls = True

        super().__init__(options=options)

    def build_children(self) -> CompositeScraperChildren:
        list_scraper = EngineManufacturersListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=self.http_policy,
                source_adapter=self.source_adapter,
                debug_dir=self.debug_dir,
            ),
        )
        indianapolis_list_scraper = IndianapolisOnlyEngineManufacturersListScraper(
            options=ScraperOptions(
                include_urls=True,
                policy=self.http_policy,
                source_adapter=self.source_adapter,
                debug_dir=self.debug_dir,
            ),
        )
        single_scraper = SingleEngineManufacturerScraper(
            options=ScraperOptions(
                policy=self.http_policy,
                source_adapter=self.source_adapter,
                debug_dir=self.debug_dir,
            ),
        )

        def get_all_records() -> list[dict[str, Any]]:
            return list_scraper.fetch() + indianapolis_list_scraper.fetch()

        records_adapter = IterableSourceAdapter(get_all_records)

        return CompositeScraperChildren(
            list_scraper=list_scraper,
            single_scraper=single_scraper,
            records_adapter=records_adapter,
        )

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
        manufacturer = record.get("manufacturer")
        if isinstance(manufacturer, dict):
            return manufacturer.get("url")
        url = record.get("manufacturer_url")
        if isinstance(url, str):
            return url
        return None

    def _parse_soup(self, _soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Metoda wymagana przez bazę - nie używana w tym scraperze."""
        msg = "Use fetch() bezpośrednio dla pełnego scrapingu"
        raise NotImplementedError(msg)


if __name__ == "__main__":
    from scrapers.base.helpers.runner import run_and_export
    from scrapers.base.run_config import RunConfig

    run_and_export(
        F1CompleteEngineManufacturerScraper,
        "engines/f1_engine_manufacturers_complete.json",
        run_config=RunConfig(output_dir=Path("../../data/wiki")),
    )
