from __future__ import annotations

from typing import Dict

from scrapers.base.F1_table_scraper import F1TableScraper
from scrapers.helpers.columns.columns import (
    UrlColumn,
    SeasonsColumn,
    IntColumn,
    LinksListColumn,
)


class F1FormerConstructorsListScraper(F1TableScraper):
    """
    Byli konstruktorzy – sekcja 'Former constructors'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Former_constructors"

    expected_headers = [
        "Constructor",
        "Licensed in",
        "Seasons",
    ]

    # nagłówek z tabeli -> klucz w dict
    column_map: Dict[str, str] = {
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

    # logika kolumn po stronie KLUCZA (po column_map)
    columns = {
        # nazwa konstruktora – pojedynczy link {text, url}
        "constructor": UrlColumn(),
        "licensed_in": LinksListColumn(),
        # sezony – parser sezonów (lista lat/zakresów)
        "seasons": SeasonsColumn(),
        # statystyki – liczby całkowite
        "races_entered": IntColumn(),
        "races_started": IntColumn(),
        "drivers": IntColumn(),
        "total_entries": IntColumn(),
        "wins": IntColumn(),
        "points": IntColumn(),
        "poles": IntColumn(),
        "fastest_laps": IntColumn(),
        "podiums": IntColumn(),
        "wcc_titles": IntColumn(),
        "wdc_titles": IntColumn(),
    }
    # "licensed_in" i "drivers" obsłuży domyślny AutoColumn z F1TableScraper


if __name__ == "__main__":
    scraper = F1FormerConstructorsListScraper(include_urls=True)

    constructors = scraper.fetch()
    print(f"Pobrano rekordów: {len(constructors)}")

    scraper.to_json("../../data/wiki/constructors/f1_former_constructors.json")
    scraper.to_csv("../../data/wiki/constructors/f1_former_constructors.csv")
