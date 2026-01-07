from pathlib import Path

from models.records.factories import build_constructor_record
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.constants import (
    CONSTRUCTOR_FASTEST_LAPS_HEADER,
    CONSTRUCTOR_PODIUMS_HEADER,
    CONSTRUCTOR_POINTS_HEADER,
    CONSTRUCTOR_POLES_HEADER,
    CONSTRUCTOR_RACES_ENTERED_HEADER,
    CONSTRUCTOR_RACES_STARTED_HEADER,
    CONSTRUCTOR_SEASONS_HEADER,
    CONSTRUCTOR_WINS_HEADER,
    FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
)


class FormerConstructorsListScraper(BaseConstructorListScraper):
    """
    Byli konstruktorzy – sekcja 'Former constructors'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    schema_columns = [
        BaseConstructorListScraper.build_licensed_in_column(),
        column(CONSTRUCTOR_SEASONS_HEADER, "seasons", SeasonsColumn()),
        column(CONSTRUCTOR_RACES_ENTERED_HEADER, "races_entered", IntColumn()),
        column(CONSTRUCTOR_RACES_STARTED_HEADER, "races_started", IntColumn()),
        column(CONSTRUCTOR_WINS_HEADER, "wins", IntColumn()),
        column(CONSTRUCTOR_POINTS_HEADER, "points", IntColumn()),
        column(CONSTRUCTOR_POLES_HEADER, "poles", IntColumn()),
        column(CONSTRUCTOR_FASTEST_LAPS_HEADER, "fastest_laps", IntColumn()),
        column(CONSTRUCTOR_PODIUMS_HEADER, "podiums", IntColumn()),
        *BaseConstructorListScraper.build_common_metadata_columns(),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Former_constructors",
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=build_constructor_record,
    )


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
