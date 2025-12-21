from __future__ import annotations

from typing import Dict

from scrapers.constructors.base import ConstructorsBaseScraper
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.run import run_and_export


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
    run_and_export(
        F1FormerConstructorsListScraper,
        "../../data/wiki/constructors/f1_former_constructors.json",
        "../../data/wiki/constructors/f1_former_constructors.csv",
        include_urls=True,
    )
