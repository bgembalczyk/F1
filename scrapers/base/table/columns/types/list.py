from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class ListColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.clean_text:
            return []
        parts = [p.strip() for p in ctx.clean_text.split(",") if p.strip()]
        return parts
