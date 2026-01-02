from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.presets import BASE_STATS_COLUMNS, BASE_STATS_MAP
from scrapers.base.table.scraper import F1TableScraper


class Constructors2025ListScraper(F1TableScraper):
    """
    Aktualni konstruktorzy – sekcja
    'Constructors for the 2025 season' z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Constructors_for_the_2025_season",
        expected_headers=[
            "Constructor",
            "Engine",
            "Licensed in",
            "Based in",
        ],
        # nagłówek z tabeli -> klucz w dict
        column_map={
            "Constructor": "constructor",
            "Engine": "engine",
            "Licensed in": "licensed_in",
            "Based in": "based_in",
            **BASE_STATS_MAP,
            "Drivers": "drivers",
            "Total Entries": "total_entries",
            "WCC": "wcc_titles",
            "WDC": "wdc_titles",
            "Antecedent teams": "antecedent_teams",
        },
        # logika kolumn po stronie KLUCZA (po column_map)
        columns={
            # nazwa konstruktora – pojedynczy link {text, url}
            "constructor": UrlColumn(),
            # silnik – lista linków [{text, url}, ...]
            "engine": LinksListColumn(),
            "based_in": LinksListColumn(),
            **BASE_STATS_COLUMNS,
            "drivers": IntColumn(),
            "total_entries": IntColumn(),
            "wcc_titles": IntColumn(),
            "wdc_titles": IntColumn(),
            # poprzednie zespoły – lista linków
            "antecedent_teams": LinksListColumn(),
        },
    )
    # pozostałe kolumny ("licensed_in", "based_in", "drivers") obsłuży domyślny AutoColumn


if __name__ == "__main__":
    run_and_export(
        Constructors2025ListScraper,
        "constructors/f1_constructors_2025.json",
        "constructors/f1_constructors_2025.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
