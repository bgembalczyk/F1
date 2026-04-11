from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.mixins.background import BackgroundMixin
from scrapers.columns.types.mixins.enum import EnumMarksMixin
from scrapers.constants_drivers import MARK_NON_CHAMPIONSHIP_EVENT
from scrapers.helpers.normalize import normalize_auto_value


class FatalityEventColumn(EnumMarksMixin, BackgroundMixin, BaseColumn):
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
