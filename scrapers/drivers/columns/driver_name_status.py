from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.bool import BoolColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.drivers.constants import (
    MARK_ACTIVE_DRIVER,
    MARK_ACTIVE_DRIVER_ALT,
    MARK_WORLD_CHAMPION,
)


class DriverNameStatusColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "driver": UrlColumn(),
                "is_active": BoolColumn(self._is_active),
                "is_world_champion": BoolColumn(self._is_world_champion),
            }
        )

    @staticmethod
    def _is_active(ctx: ColumnContext) -> bool:
        return (ctx.raw_text or "").strip().endswith(
            (MARK_ACTIVE_DRIVER, MARK_ACTIVE_DRIVER_ALT)
        )

    @staticmethod
    def _is_world_champion(ctx: ColumnContext) -> bool:
        return (ctx.raw_text or "").strip().endswith(
            (MARK_ACTIVE_DRIVER, MARK_WORLD_CHAMPION)
        )
