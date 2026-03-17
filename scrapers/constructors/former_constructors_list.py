from pathlib import Path

from models.records.factories import build_constructor_record
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.constants import CONSTRUCTOR_FASTEST_LAPS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_PODIUMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POINTS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POLES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_ENTERED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_STARTED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_SEASONS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WINS_HEADER
from scrapers.constructors.constants import FORMER_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.sections import ConstructorsListSectionParser


class FormerConstructorsListScraper(BaseConstructorListScraper):
    """
    Byli konstruktorzy - sekcja 'Former constructors'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    schema_columns = [
        *BaseConstructorListScraper.build_common_metadata_columns(),
        BaseConstructorListScraper.build_licensed_in_column(),
        column(CONSTRUCTOR_SEASONS_HEADER, "seasons", SeasonsColumn()),
        column(CONSTRUCTOR_RACES_ENTERED_HEADER, "races_entered", IntColumn()),
        column(CONSTRUCTOR_RACES_STARTED_HEADER, "races_started", IntColumn()),
        column(CONSTRUCTOR_WINS_HEADER, "wins", IntColumn()),
        column(CONSTRUCTOR_POINTS_HEADER, "points", IntColumn()),
        column(CONSTRUCTOR_POLES_HEADER, "poles", IntColumn()),
        column(CONSTRUCTOR_FASTEST_LAPS_HEADER, "fastest_laps", IntColumn()),
        column(CONSTRUCTOR_PODIUMS_HEADER, "podiums", IntColumn()),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Former_constructors",
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=build_constructor_record,
    )

    section_label = "Former constructors"
    section_parser_class = ConstructorsListSectionParser

if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.constructors.former_constructors_list")
