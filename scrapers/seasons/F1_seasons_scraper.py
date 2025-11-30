from scrapers.F1_table_scraper import F1TableScraper


class F1SeasonsScraper(F1TableScraper):
    """
    Scraper listy sezonów z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_seasons
    (główna tabela World Championship seasons)
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_seasons"
    # jeśli id sekcji się kiedyś zmieni – poprawiasz tylko to
    section_id = "Seasons"

    # nagłówki, które MUSZĄ wystąpić w tabeli
    expected_headers = [
        "Season",
        "Races",
    ]

    # mapowanie: nagłówek z tabeli -> klucz w dict wynikowym
    column_map = {
        "Season": "season",
        "Races": "races",
        "Drivers' Champion (team)": "drivers_champion_team",
        "Constructors' Champion": "constructors_champion",
    }

    # typy kolumn po STRONIE KLUCZA (po column_map)
    # - "season" jako pojedynczy link {text, url}
    # - pozostałe kolumny z mistrzami jako lista linków [{text, url}, ...]
    column_types = {
        "season": "link",
        "drivers_champion_team": "list_of_links",
        "constructors_champion": "list_of_links",
        # "races" zostawiamy jako "auto" -> powinno zparsować się do int
    }


if __name__ == "__main__":
    scraper = F1SeasonsScraper(include_urls=True)

    seasons = scraper.fetch()
    print(f"Pobrano rekordów: {len(seasons)}")

    scraper.to_json("../../data/wiki/seasons/f1_seasons.json")
    scraper.to_csv("../../data/wiki/seasons/f1_seasons.csv")
