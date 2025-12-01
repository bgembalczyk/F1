from scrapers.F1_table_scraper import F1TableScraper


class F1Constructors2025Scraper(F1TableScraper):
    """
    Aktualni konstruktorzy – sekcja
    'Constructors for the 2025 season' z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Constructors_for_the_2025_season"

    expected_headers = [
        "Constructor",
        "Engine",
        "Licensed in",
        "Based in",
    ]

    # nagłówek z tabeli -> klucz w dict
    column_map = {
        "Constructor": "constructor",
        "Engine": "engine",
        "Licensed in": "licensed_in",
        "Based in": "based_in",
        "Seasons": "seasons",
        "Races Entered": "races_entered",
        "Races Started": "races_started",
        "Drivers": "drivers",
        "Total Entries": "total_entries",
        "Wins": "wins",
        "Points": "points",
        "Poles": "poles",
        "FL": "fastest_laps",
        "Podiums": "podiums",
        "WCC": "wcc_titles",
        "WDC": "wdc_titles",
        "Antecedent teams": "antecedent_teams",
    }

    # typy kolumn po STRONIE KLUCZA (po column_map)
    column_types = {
        # główny link do konstruktora
        "constructor": "link",
        # sezony startów – lista dictów {year, url}
        "seasons": "seasons",
        # silniki / kierowcy / poprzednie zespoły – listy linków
        "engine": "list_of_links",
        "drivers": "list_of_links",
        "antecedent_teams": "list_of_links",
        # państwa możemy spokojnie zrzucić do czystego tekstu
        "licensed_in": "text",
        "based_in": "text",
        # reszta zostaje na "auto" – liczby zparsują się do int/float
    }


if __name__ == "__main__":
    scraper = F1Constructors2025Scraper(include_urls=True)

    constructors = scraper.fetch()
    print(f"Pobrano rekordów: {len(constructors)}")

    scraper.to_json("../../data/wiki/constructors/f1_constructors_2025.json")
    scraper.to_csv("../../data/wiki/constructors/f1_constructors_2025.csv")
