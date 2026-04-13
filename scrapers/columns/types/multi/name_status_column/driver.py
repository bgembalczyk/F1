from scrapers.columns.context import ColumnContext
from scrapers.columns.types.multi.name_status_column.base import NameStatusColumn
from scrapers.constants.constants_drivers import MARK_ACTIVE_DRIVER
from scrapers.constants.constants_drivers import MARK_ACTIVE_WORLD_CHAMPION
from scrapers.constants.constants_drivers import MARK_WORLD_CHAMPION


class DriverNameStatusColumn(NameStatusColumn):
    """
    Column for driver name with active and world champion status markers.

    Extracts:
    - driver: Driver name with URL
    - is_active: True if name ends with MARK_ACTIVE_DRIVER (~)
      or MARK_ACTIVE_DRIVER_ALT (*)
    - is_world_champion: True if name ends with MARK_WORLD_CHAMPION (^)
    """

    ACTIVE_MARKS = {
        MARK_ACTIVE_DRIVER: True,
        MARK_ACTIVE_WORLD_CHAMPION: True,
    }
    WORLD_CHAMPION_MARKS = {
        MARK_WORLD_CHAMPION: True,
        MARK_ACTIVE_WORLD_CHAMPION: True,
    }

    def __init__(self) -> None:
        super().__init__(
            entity_key="driver",
            status_extractors={
                "is_active": self._is_active,
                "is_world_champion": self._is_world_champion,
            },
        )

    def _is_active(self, ctx: ColumnContext) -> bool:
        return bool(self.parse_marks(ctx, mapping=self.ACTIVE_MARKS, default=False))

    def _is_world_champion(self, ctx: ColumnContext) -> bool:
        return bool(
            self.parse_marks(
                ctx,
                mapping=self.WORLD_CHAMPION_MARKS,
                default=False,
            ),
        )


__all__ = ["DriverNameStatusColumn"]
