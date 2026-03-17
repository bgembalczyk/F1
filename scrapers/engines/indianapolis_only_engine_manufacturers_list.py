from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper
from scrapers.base.run_config import RunConfig


class IndianapolisOnlyEngineManufacturersListScraper(IndianapolisOnlyListScraper):
    """
    Lista 'Indianapolis 500 only' dla producentów silników.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers"
    record_key = "manufacturer"
    url_key = "manufacturer_url"

if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.engines.indianapolis_only_engine_manufacturers_list")
