from F1_table_scraper import F1TableScraper


class F1SeasonsScraper(F1TableScraper):
    """
    Scraper listy sezonów z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_seasons
    (główna tabela World Championship seasons)
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_seasons"
    # jeśli id sekcji się kiedyś zmieni – poprawiasz tylko to
    section_id = "World_Championship_seasons"

    expected_headers = [
        "Season",
        "Races",
    ]

    column_map = {
        "Season": "season",
        "Races": "races",
        "Drivers' Champion (team)": "drivers_champion_team",
        "Constructors' Champion": "constructors_champion",
    }

    url_columns = ("Season",)


if __name__ == "__main__":
    scraper = F1SeasonsScraper(include_urls=True)

    seasons = scraper.fetch()
    print(f"Pobrano rekordów: {len(seasons)}")

    scraper.to_json("f1_seasons.json")
    scraper.to_csv("f1_seasons.csv")

    # opcjonalnie:
    # df = scraper.to_dataframe()
    # print(df.head())
