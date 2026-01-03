from pathlib import Path

from models.records.factories import build_constructor_record
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.constructors.constants import (
    CONSTRUCTOR_HEADER,
    DRIVERS_HEADER,
    FASTEST_LAPS_HEADER,
    FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
    LICENSED_IN_HEADER,
    PODIUMS_HEADER,
    POINTS_HEADER,
    POLES_HEADER,
    RACES_ENTERED_HEADER,
    RACES_STARTED_HEADER,
    SEASONS_HEADER,
    TOTAL_ENTRIES_HEADER,
    WCC_HEADER,
    WDC_HEADER,
    WINS_HEADER,
)


class FormerConstructorsListScraper(F1TableScraper):
    """
    Byli konstruktorzy – sekcja 'Former constructors'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Former_constructors",
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        # nagłówek z tabeli -> klucz w dict
        column_map={
            CONSTRUCTOR_HEADER: "constructor",
            LICENSED_IN_HEADER: "licensed_in",
            SEASONS_HEADER: "seasons",
            RACES_ENTERED_HEADER: "races_entered",
            RACES_STARTED_HEADER: "races_started",
            DRIVERS_HEADER: "drivers",
            TOTAL_ENTRIES_HEADER: "total_entries",
            WINS_HEADER: "wins",
            POINTS_HEADER: "points",
            POLES_HEADER: "poles",
            FASTEST_LAPS_HEADER: "fastest_laps",
            PODIUMS_HEADER: "podiums",
            WCC_HEADER: "wcc_titles",
            WDC_HEADER: "wdc_titles",
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
        record_factory=build_constructor_record,
    )
    # "licensed_in" i "drivers" obsłuży domyślny AutoColumn z F1TableScraper

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.normalize_empty_values = False
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    run_and_export(
        FormerConstructorsListScraper,
        "constructors/f1_former_constructors.json",
        "constructors/f1_former_constructors.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
