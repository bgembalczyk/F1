from scrapers.F1_table_scraper import F1TableScraper


class F1FormerConstructorsScraper(F1TableScraper):
    """
    Byli konstruktorzy – sekcja 'Former constructors'
    z tej samej strony.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Former_constructors"

    expected_headers = [
        "Constructor",
        "Licensed in",
        "Seasons",
    ]

    column_map = {
        "Constructor": "constructor",
        "Licensed in": "licensed_in",
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
    }

    url_columns = ("Constructor",)


if __name__ == "__main__":
    scraper = F1FormerConstructorsScraper(include_urls=True)

    constructors = scraper.fetch()
    print(f"Pobrano rekordów: {len(constructors)}")

    scraper.to_json("f1_former_constructors.json")
    scraper.to_csv("f1_former_constructors.csv")
