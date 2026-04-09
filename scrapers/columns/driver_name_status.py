from scrapers.base.table.columns.types.name_status import NameStatusColumn
from scrapers.base.table.columns.types.name_status import create_suffix_checker
from scrapers.drivers.constants_drivers import MARK_ACTIVE_DRIVER
from scrapers.drivers.constants_drivers import MARK_ACTIVE_WORLD_CHAMPION
from scrapers.drivers.constants_drivers import MARK_WORLD_CHAMPION


class DriverNameStatusColumn(NameStatusColumn):
    """
    Column for driver name with active and world champion status markers.

    Extracts:
    - driver: Driver name with URL
    - is_active: True if name ends with MARK_ACTIVE_DRIVER (~)
      or MARK_ACTIVE_DRIVER_ALT (*)
    - is_world_champion: True if name ends with MARK_WORLD_CHAMPION (^)
    """

    def __init__(self) -> None:
        super().__init__(
            entity_key="driver",
            status_extractors={
                "is_active": create_suffix_checker(
                    MARK_ACTIVE_DRIVER,
                    MARK_ACTIVE_WORLD_CHAMPION,
                ),
                "is_world_champion": create_suffix_checker(
                    MARK_WORLD_CHAMPION,
                    MARK_ACTIVE_WORLD_CHAMPION,
                ),
            },
        )
