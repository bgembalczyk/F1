from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.constructors.base_constructor_list_scraper import BaseConstructorListScraper
from scrapers.constructors.constants import CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_BASED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_ENGINE_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_FASTEST_LAPS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_PODIUMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POINTS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POLES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_ENTERED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_STARTED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_SEASONS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WINS_HEADER


def build_current_constructors_schema() -> TableSchemaDSL:
    return TableSchemaDSL(
        columns=[
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
        ],
    )


def build_former_constructors_schema() -> TableSchemaDSL:
    return TableSchemaDSL(
        columns=[
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
        ],
    )
