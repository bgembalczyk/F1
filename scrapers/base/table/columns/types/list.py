from typing import Any

from scrapers.base.helpers.text import split_delimited_text
from scrapers.base.helpers.parsing import split_delimited_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn


@column_type_registry.register("list")
class ListColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.clean_text:
            return []
        return split_delimited_text(ctx.clean_text)
