from __future__ import annotations

from typing import Dict

from scrapers.constructors.base import ConstructorsBaseScraper


class F1FormerConstructorsListScraper(ConstructorsBaseScraper):
    """
    Byli konstruktorzy – sekcja 'Former constructors'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    section_id = "Former_constructors"

    expected_headers = [
        "Constructor",
        "Licensed in",
        "Seasons",
    ]

    # nagłówek z tabeli -> klucz w dict
    column_map: Dict[str, str] = ConstructorsBaseScraper.column_map
    # pozostałe kolumny korzystają ze wspólnej logiki bazowej


if __name__ == "__main__":
    scraper = F1FormerConstructorsListScraper(include_urls=True)

    constructors = scraper.fetch()
    print(f"Pobrano rekordów: {len(constructors)}")

    scraper.to_json("../../data/wiki/constructors/f1_former_constructors.json")
    scraper.to_csv("../../data/wiki/constructors/f1_former_constructors.csv")
