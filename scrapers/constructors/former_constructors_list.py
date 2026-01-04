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
from scrapers.base.table.dsl import TableSchemaDSL, column
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

    schema_columns = [
        column(CONSTRUCTOR_HEADER, "constructor", UrlColumn()),
        column(LICENSED_IN_HEADER, "licensed_in", LinksListColumn()),
        column(SEASONS_HEADER, "seasons", SeasonsColumn()),
        column(RACES_ENTERED_HEADER, "races_entered", IntColumn()),
        column(RACES_STARTED_HEADER, "races_started", IntColumn()),
        column(DRIVERS_HEADER, "drivers", IntColumn()),
        column(TOTAL_ENTRIES_HEADER, "total_entries", IntColumn()),
        column(WINS_HEADER, "wins", IntColumn()),
        column(POINTS_HEADER, "points", IntColumn()),
        column(POLES_HEADER, "poles", IntColumn()),
        column(FASTEST_LAPS_HEADER, "fastest_laps", IntColumn()),
        column(PODIUMS_HEADER, "podiums", IntColumn()),
        column(WCC_HEADER, "wcc_titles", IntColumn()),
        column(WDC_HEADER, "wdc_titles", IntColumn()),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Former_constructors",
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
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
