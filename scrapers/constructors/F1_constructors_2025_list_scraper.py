from __future__ import annotations

from typing import Dict

from scrapers.base.registry import register_scraper
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.run import run_and_export


@register_scraper(
    "constructors_2025",
    "constructors/f1_constructors_2025.json",
    "constructors/f1_constructors_2025.csv",
)
class F1Constructors2025ListScraper(F1TableScraper):
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
    column_map: Dict[str, str] = {
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

    # logika kolumn po stronie KLUCZA (po column_map)
    columns = {
        # nazwa konstruktora – pojedynczy link {text, url}
        "constructor": UrlColumn(),
        # silnik – lista linków [{text, url}, ...]
        "engine": LinksListColumn(),
        "based_in": LinksListColumn(),
        # sezony – standardowy parser sezonów
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
        # poprzednie zespoły – lista linków
        "antecedent_teams": LinksListColumn(),
    }
    # pozostałe kolumny ("licensed_in", "based_in", "drivers") obsłuży domyślny AutoColumn


if __name__ == "__main__":
    run_and_export(
        F1Constructors2025ListScraper,
        "../../data/wiki/constructors/f1_constructors_2025.json",
        "../../data/wiki/constructors/f1_constructors_2025.csv",
    )
