from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn


@column_type_registry.register("skip")
class SkipColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.skip_sentinel
