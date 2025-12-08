from __future__ import annotations

from typing import Dict

from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper


class ConstructorsBaseScraper(F1TableScraper):
    """Wspólna konfiguracja dla scraperów tabel konstruktorów F1."""

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"

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

    columns = {
        # nazwa konstruktora – pojedynczy link {text, url}
        "constructor": UrlColumn(),
        "licensed_in": LinksListColumn(),
        # pola specyficzne dla wybranych tabel – trzymamy tu, aby zachować spójność typów
        "engine": LinksListColumn(),
        "based_in": LinksListColumn(),
        "antecedent_teams": LinksListColumn(),
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
