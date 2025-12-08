from typing import Protocol, Any

from scrapers.base.table.columns.context import ColumnContext


class ColumnType(Protocol):
    def parse(self, ctx: ColumnContext) -> Any: ...
