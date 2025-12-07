from typing import Protocol, Any

from scrapers.base.table.helpers.columns.context import ColumnContext


class ColumnType(Protocol):
    def parse(self, ctx: ColumnContext) -> Any: ...
