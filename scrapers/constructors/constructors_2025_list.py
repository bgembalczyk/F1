from pathlib import Path

from models.records.factories import build_constructor_record
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.table.presets import BASE_STATS_COLUMNS, BASE_STATS_MAP
from scrapers.base.table.scraper import F1TableScraper
from scrapers.constructors.constants import (
    ANTECEDENT_TEAMS_HEADER,
    BASED_IN_HEADER,
    CONSTRUCTOR_HEADER,
    CONSTRUCTORS_2025_EXPECTED_HEADERS,
    DRIVERS_HEADER,
    ENGINE_HEADER,
    LICENSED_IN_HEADER,
    TOTAL_ENTRIES_HEADER,
    WCC_HEADER,
    WDC_HEADER,
)


class Constructors2025ListScraper(F1TableScraper):
    """
    Aktualni konstruktorzy – sekcja
    'Constructors for the 2025 season' z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    schema_columns = [
        column(CONSTRUCTOR_HEADER, "constructor", UrlColumn()),
        column(ENGINE_HEADER, "engine", LinksListColumn()),
        column(LICENSED_IN_HEADER, "licensed_in", AutoColumn()),
        column(BASED_IN_HEADER, "based_in", LinksListColumn()),
        *[
            column(
                header,
                {"wcc": "wcc_titles", "wdc": "wdc_titles"}.get(key, key),
                BASE_STATS_COLUMNS[key],
            )
            for header, key in BASE_STATS_MAP.items()
        ],
        column(DRIVERS_HEADER, "drivers", IntColumn()),
        column(TOTAL_ENTRIES_HEADER, "total_entries", IntColumn()),
        column(WCC_HEADER, "wcc_titles", IntColumn()),
        column(WDC_HEADER, "wdc_titles", IntColumn()),
        column(ANTECEDENT_TEAMS_HEADER, "antecedent_teams", LinksListColumn()),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Constructors_for_the_2025_season",
        expected_headers=CONSTRUCTORS_2025_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=build_constructor_record,
    )
    # pozostałe kolumny ("licensed_in", "based_in", "drivers") obsłuży domyślny AutoColumn

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
        Constructors2025ListScraper,
        "constructors/f1_constructors_2025.json",
        "constructors/f1_constructors_2025.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
