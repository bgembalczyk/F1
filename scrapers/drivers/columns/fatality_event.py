from typing import Any

from scrapers.base.helpers.normalize import normalize_auto_value
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types.background_mixin import BackgroundMixin
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.columns.types.enum_marks import EnumMarksMixin
from scrapers.drivers.constants import MARK_NON_CHAMPIONSHIP_EVENT


class FatalityEventColumn(EnumMarksMixin, BackgroundMixin, BaseColumn):
    def __init__(self, auto_column: AutoColumn | None = None) -> None:
        super().__init__(
            mapping={MARK_NON_CHAMPIONSHIP_EVENT: False},
            default=True,
        )
        self.auto_column = auto_column or AutoColumn()

    def parse(self, ctx: ColumnContext) -> Any:
        championship = EnumMarksMixin.parse(self, ctx)
        auto_value = self.auto_column.parse(ctx)
        normalized = normalize_auto_value(auto_value, strip_marks=True)
        return {"event": normalized, "championship": championship}
