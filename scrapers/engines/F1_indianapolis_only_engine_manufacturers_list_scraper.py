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
    scraper = F1IndianapolisOnlyEngineManufacturersListScraper(include_urls=True)

    indy_engines = scraper.fetch()
    print(f"Pobrano rekordów: {len(indy_engines)}")

    scraper.to_json(
        "../../data/wiki/engines/f1_indianapolis_only_engine_manufacturers.json"
    )
    scraper.to_csv(
        "../../data/wiki/engines/f1_indianapolis_only_engine_manufacturers.csv"
    )

    # opcjonalnie:
    # for e in indy_engines:
    #     print(e)
    # df = scraper.to_dataframe()
    # print(df.head())
