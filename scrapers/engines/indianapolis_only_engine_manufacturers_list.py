from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper


class IndianapolisOnlyEngineManufacturersListScraper(IndianapolisOnlyListScraper):
    """
    Lista 'Indianapolis 500 only' dla producentów silników.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers"
    record_key = "manufacturer"
    url_key = "manufacturer_url"


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
