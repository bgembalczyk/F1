from __future__ import annotations

from typing import Dict

from scrapers.constructors.base import ConstructorsBaseScraper


class F1Constructors2025ListScraper(ConstructorsBaseScraper):
    """
    Aktualni konstruktorzy – sekcja
    'Constructors for the 2025 season' z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    section_id = "Constructors_for_the_2025_season"

    expected_headers = [
        "Constructor",
        "Engine",
        "Licensed in",
        "Based in",
    ]

    # nagłówek z tabeli -> klucz w dict
    column_map: Dict[str, str] = {
        **ConstructorsBaseScraper.column_map,
        "Engine": "engine",
        "Based in": "based_in",
        "Antecedent teams": "antecedent_teams",
    }
    # pozostałe kolumny ("licensed_in", "drivers") korzystają z logiki bazowej


if __name__ == "__main__":
    scraper = F1Constructors2025ListScraper(include_urls=True)

    constructors = scraper.fetch()
    print(f"Pobrano rekordów: {len(constructors)}")

    scraper.to_json("../../data/wiki/constructors/f1_constructors_2025.json")
    scraper.to_csv("../../data/wiki/constructors/f1_constructors_2025.csv")
