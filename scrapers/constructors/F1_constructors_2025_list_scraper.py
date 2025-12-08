from __future__ import annotations

from typing import Dict

from scrapers.constructors.base import ConstructorsBaseScraper
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.run import run_and_export


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
    run_and_export(
        F1Constructors2025ListScraper,
        "../../data/wiki/constructors/f1_constructors_2025.json",
        "../../data/wiki/constructors/f1_constructors_2025.csv",
        include_urls=True,
    )
