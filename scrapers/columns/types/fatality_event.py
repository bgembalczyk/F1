from typing import Any

from scrapers.columns.context import ColumnContext
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.background_column import BackgroundColumn
from scrapers.columns.types.enum_marks_column import EnumMarksColumn
from scrapers.constants.constants_drivers import MARK_NON_CHAMPIONSHIP_EVENT
from scrapers.helpers.normalize import normalize_auto_value


class FatalityEventColumn(EnumMarksColumn, BackgroundColumn):
    def __init__(self, auto_column: AutoColumn | None = None) -> None:
        super().__init__(
            mapping={MARK_NON_CHAMPIONSHIP_EVENT: False},
            default=True,
        )
        self.auto_column = auto_column or AutoColumn()

    def parse(self, ctx: ColumnContext) -> Any:
        championship = self.parse_marks(ctx)
        auto_value = self.auto_column.parse(ctx)
        normalized = normalize_auto_value(auto_value, strip_marks=True)
        return {"event": normalized, "championship": championship}
