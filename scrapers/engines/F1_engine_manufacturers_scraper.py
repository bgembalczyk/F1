from scrapers.F1_table_scraper import F1TableScraper


class F1EngineManufacturersScraper(F1TableScraper):
    """
    Tabela 'Engine manufacturers' ze strony:
    https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers"
    section_id = "Engine_manufacturers"

    expected_headers = [
        "Manufacturer",
        "Engines built in",
        "Seasons",
    ]

    column_map = {
        "Manufacturer": "manufacturer",
        "Engines built in": "engines_built_in",
        "Seasons": "seasons",
        "Races Entered": "races_entered",
        "Races Started": "races_started",
        "Wins": "wins",
        "Points": "points",
        "Poles": "poles",
        "FL": "fastest_laps",
        "Podiums": "podiums",
        "WCC": "wcc_titles",
        "WDC": "wdc_titles",
    }

    url_columns = ("Manufacturer",)


if __name__ == "__main__":
    scraper = F1EngineManufacturersScraper(include_urls=True)

    engines = scraper.fetch()
    print(f"Pobrano rekordów: {len(engines)}")

    scraper.to_json("f1_engine_manufacturers.json")
    scraper.to_csv("f1_engine_manufacturers.csv")

    # opcjonalnie:
    # df = scraper.to_dataframe()
    # print(df.head())
