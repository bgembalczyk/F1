from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext


class TextColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.clean_text or None


__all__ = ["TextColumn"]
