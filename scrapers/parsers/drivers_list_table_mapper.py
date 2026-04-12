from typing import Any

from scrapers.constants_drivers import DRIVER_CHAMPIONSHIPS_HEADER
from scrapers.constants_drivers import DRIVER_FASTEST_LAPS_HEADER
from scrapers.constants_drivers import DRIVER_NAME_HEADER
from scrapers.constants_drivers import DRIVER_NATIONALITY_HEADER
from scrapers.constants_drivers import DRIVER_PODIUMS_HEADER
from scrapers.constants_drivers import DRIVER_POINTS_HEADER
from scrapers.constants_drivers import DRIVER_POLE_POSITIONS_HEADER
from scrapers.constants_drivers import DRIVER_RACE_ENTRIES_HEADER
from scrapers.constants_drivers import DRIVER_RACE_STARTS_HEADER
from scrapers.constants_drivers import DRIVER_RACE_WINS_HEADER
from scrapers.constants_drivers import DRIVER_SEASONS_COMPETED_HEADER
from scrapers.constants_drivers import DRIVERS_LIST_HEADERS
from scrapers.parsers.wiki.driver_ordered_table_mapper import DriverOrderedTableMapper


class DriversListTableMapper(DriverOrderedTableMapper):
    table_type = "drivers_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        DRIVER_NAME_HEADER: "driver",
        DRIVER_NATIONALITY_HEADER: "nationality",
        DRIVER_SEASONS_COMPETED_HEADER: "seasons_competed",
        DRIVER_CHAMPIONSHIPS_HEADER: "drivers_championships",
        DRIVER_RACE_ENTRIES_HEADER: "race_entries",
        DRIVER_RACE_STARTS_HEADER: "race_starts",
        DRIVER_POLE_POSITIONS_HEADER: "pole_positions",
        DRIVER_RACE_WINS_HEADER: "race_wins",
        DRIVER_PODIUMS_HEADER: "podiums",
        DRIVER_FASTEST_LAPS_HEADER: "fastest_laps",
        DRIVER_POINTS_HEADER: "points",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = set(DRIVERS_LIST_HEADERS)
        return required_headers.issubset(set(headers))
