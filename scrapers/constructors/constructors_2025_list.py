from pathlib import Path

from models.records.factories import build_constructor_record
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
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

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Constructors_for_the_2025_season",
        expected_headers=CONSTRUCTORS_2025_EXPECTED_HEADERS,
        # nagłówek z tabeli -> klucz w dict
        column_map={
            CONSTRUCTOR_HEADER: "constructor",
            ENGINE_HEADER: "engine",
            LICENSED_IN_HEADER: "licensed_in",
            BASED_IN_HEADER: "based_in",
            **BASE_STATS_MAP,
            DRIVERS_HEADER: "drivers",
            TOTAL_ENTRIES_HEADER: "total_entries",
            WCC_HEADER: "wcc_titles",
            WDC_HEADER: "wdc_titles",
            ANTECEDENT_TEAMS_HEADER: "antecedent_teams",
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
