from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListConfig
from scrapers.base.list.indianapolis_only_scraper import (
    build_indianapolis_only_list_scraper,
)

CONFIG = IndianapolisOnlyListConfig(
    url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
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
