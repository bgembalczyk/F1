from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class TextColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.clean_text or None
