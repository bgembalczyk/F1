from scrapers.base.list.scrapper import F1ListScraper


class F1IndianapolisOnlyEngineManufacturersListScraper(F1ListScraper):
    """
    Lista 'Indianapolis 500 only' dla producentów silników.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers"
    section_id = "Indianapolis_500_only"

    record_key = "manufacturer"
    url_key = "manufacturer_url"


if __name__ == "__main__":
    from main import main

    main()
