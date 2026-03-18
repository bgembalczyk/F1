from typing import Any

from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.engines.single_scraper import SingleEngineManufacturerScraper


class F1CompleteEngineManufacturerDataExtractor(CompositeDataExtractor):
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

    def build_children(self) -> CompositeDataExtractorChildren:
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

        return CompositeDataExtractorChildren(
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


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
