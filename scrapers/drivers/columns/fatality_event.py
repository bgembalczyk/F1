from typing import Any

from scrapers.base.helpers.normalize import normalize_auto_value
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn


class FatalityEventColumn(BaseColumn):
    def __init__(self, auto_column: AutoColumn | None = None) -> None:
        self.auto_column = auto_column or AutoColumn()

    def parse(self, ctx: ColumnContext) -> Any:
        championship = "†" not in (ctx.raw_text or "")
        auto_value = self.auto_column.parse(ctx)
        normalized = normalize_auto_value(auto_value, strip_marks=True)
        return {"event": normalized, "championship": championship}
