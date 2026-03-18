from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListConfig
from scrapers.base.list.indianapolis_only_scraper import build_indianapolis_only_list_scraper

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
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.constructors.indianapolis_only_constructors_list")
