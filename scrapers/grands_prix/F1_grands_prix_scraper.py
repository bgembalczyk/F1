from scrapers.F1_table_scraper import F1TableScraper


class F1GrandsPrixScraper(F1TableScraper):
    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix"
    section_id = "By_race_title"

    expected_headers = [
        "Race title",
        "Years held",
    ]

    column_map = {
        "Race title": "race_title",
        "Years held": "years_held",
        "Races held": "races_held",
    }

    url_columns = ("Race title",)


if __name__ == "__main__":
    scraper = F1GrandsPrixScraper(include_urls=True)

    races = scraper.fetch()
    print(f"Pobrano rekordów: {len(races)}")

    scraper.to_json("f1_grands_prix_by_title.json")
    scraper.to_csv("f1_grands_prix_by_title.csv")

    # opcjonalnie:
    # df = scraper.to_dataframe()
    # print(df.head())
