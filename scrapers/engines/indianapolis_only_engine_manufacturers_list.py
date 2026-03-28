from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListConfig
from scrapers.base.list.indianapolis_only_scraper import (
    build_indianapolis_only_list_scraper,
)
from scrapers.base.source_catalog import ENGINES_LIST

CONFIG = IndianapolisOnlyListConfig(
    url=ENGINES_LIST.base_url,
    record_key="manufacturer",
    url_key="manufacturer_url",
    domain_name="engines",
    record_type="manufacturer",
)

IndianapolisOnlyEngineManufacturersListScraper = build_indianapolis_only_list_scraper(
    class_name="IndianapolisOnlyEngineManufacturersListScraper",
    config=CONFIG,
)


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
