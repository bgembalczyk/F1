from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.drivers.columns.driver_name_status import DriverNameStatusColumn
from scrapers.drivers.constants import DRIVER_CHAMPIONSHIPS_HEADER
from scrapers.drivers.constants import DRIVER_FASTEST_LAPS_HEADER
from scrapers.drivers.constants import DRIVER_NAME_HEADER
from scrapers.drivers.constants import DRIVER_NATIONALITY_HEADER
from scrapers.drivers.constants import DRIVER_PODIUMS_HEADER
from scrapers.drivers.constants import DRIVER_POINTS_HEADER
from scrapers.drivers.constants import DRIVER_POLE_POSITIONS_HEADER
from scrapers.drivers.constants import DRIVER_RACE_ENTRIES_HEADER
from scrapers.drivers.constants import DRIVER_RACE_STARTS_HEADER
from scrapers.drivers.constants import DRIVER_RACE_WINS_HEADER
from scrapers.drivers.constants import DRIVER_SEASONS_COMPETED_HEADER


def build_drivers_list_schema() -> TableSchemaDSL:
    return TableSchemaDSL(
        columns=[
            column(DRIVER_NAME_HEADER, "driver", DriverNameStatusColumn()),
            column(DRIVER_NATIONALITY_HEADER, "nationality", TextColumn()),
            column(DRIVER_SEASONS_COMPETED_HEADER, "seasons_competed", SeasonsColumn()),
            column(DRIVER_CHAMPIONSHIPS_HEADER, "drivers_championships", TextColumn()),
            column(DRIVER_RACE_ENTRIES_HEADER, "race_entries", IntColumn()),
            column(DRIVER_RACE_STARTS_HEADER, "race_starts", IntColumn()),
            column(DRIVER_POLE_POSITIONS_HEADER, "pole_positions", IntColumn()),
            column(DRIVER_RACE_WINS_HEADER, "race_wins", IntColumn()),
            column(DRIVER_PODIUMS_HEADER, "podiums", IntColumn()),
            column(DRIVER_FASTEST_LAPS_HEADER, "fastest_laps", IntColumn()),
            column(DRIVER_POINTS_HEADER, "points", TextColumn()),
        ],
    )
