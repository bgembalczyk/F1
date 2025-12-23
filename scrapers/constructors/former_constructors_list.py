from __future__ import annotations

from pathlib import Path

from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper


class FormerConstructorsListScraper(F1TableScraper):
    """
    Byli konstruktorzy – sekcja 'Former constructors'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Former_constructors",
        expected_headers=[
            "Constructor",
            "Licensed in",
            "Seasons",
        ],
        # nagłówek z tabeli -> klucz w dict
        column_map={
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
        },
        # logika kolumn po stronie KLUCZA (po column_map)
        columns={
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
        },
    )
    # "licensed_in" i "drivers" obsłuży domyślny AutoColumn z F1TableScraper


if __name__ == "__main__":
    run_and_export(
        FormerConstructorsListScraper,
        "constructors/f1_former_constructors.json",
        "constructors/f1_former_constructors.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
