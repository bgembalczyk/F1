from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListConfig
from scrapers.base.list.indianapolis_only_scraper import (
    build_indianapolis_only_list_scraper,
)
from scrapers.base.source_catalog import CONSTRUCTORS_LIST

CONFIG = IndianapolisOnlyListConfig(
    url=CONSTRUCTORS_LIST.base_url,
    record_key="constructor",
    url_key="constructor_url",
    domain_name="constructors",
    record_type="constructor",
)

IndianapolisOnlyConstructorsListScraper = build_indianapolis_only_list_scraper(
    class_name="IndianapolisOnlyConstructorsListScraper",
    config=CONFIG,
)


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
