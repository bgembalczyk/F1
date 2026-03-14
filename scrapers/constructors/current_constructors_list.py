from datetime import datetime
from datetime import timezone
from pathlib import Path

from models.records.factories import build_constructor_record
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.constants import CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_BASED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_ENGINE_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors.constants import CURRENT_CONSTRUCTORS_EXPECTED_HEADERS

CURRENT_YEAR = datetime.now(tz=timezone.utc).year


class CurrentConstructorsListScraper(BaseConstructorListScraper):
    """
    Aktualni konstruktorzy - sekcja
    'Constructors for the current season' z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    schema_columns = [
        column(CONSTRUCTOR_ENGINE_HEADER, "engine", LinksListColumn()),
        column(CONSTRUCTOR_LICENSED_IN_HEADER, "licensed_in", AutoColumn()),
        column(CONSTRUCTOR_BASED_IN_HEADER, "based_in", LinksListColumn()),
        *BaseConstructorListScraper.build_common_stats_columns(),
        column(CONSTRUCTOR_DRIVERS_HEADER, "drivers", AutoColumn()),
        *BaseConstructorListScraper.build_common_metadata_columns(),
        column(
            CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER,
            "antecedent_teams",
            LinksListColumn(),
        ),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id=f"Constructors_for_the_{CURRENT_YEAR}_season",
        expected_headers=CURRENT_CONSTRUCTORS_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=build_constructor_record,
    )


if __name__ == "__main__":
    run_and_export(
        CurrentConstructorsListScraper,
        f"constructors/f1_constructors_{CURRENT_YEAR}.json",
        f"constructors/f1_constructors_{CURRENT_YEAR}.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
