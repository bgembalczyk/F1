from complete_extractor.base import CompleteExtractorBase
from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.engines.single_scraper import SingleEngineManufacturerScraper


class F1CompleteEngineManufacturerDataExtractor(CompleteExtractorBase):
    """
    Pobiera listę producentów silników z wielu źródeł, a następnie zaciąga
    wszystkie infoboksy i tabele z artykułu każdego producenta.
    """

    url = EngineManufacturersListScraper.CONFIG.url
    DOMAIN_CONFIG = CompleteExtractorDomainConfig(
        list_scraper_clses=(
            EngineManufacturersListScraper,
            IndianapolisOnlyEngineManufacturersListScraper,
        ),
        single_scraper_cls=SingleEngineManufacturerScraper,
        detail_url_field_paths=("manufacturer.url", "manufacturer_url"),
    )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
