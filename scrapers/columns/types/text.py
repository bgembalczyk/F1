from typing import Any

from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext


class TextColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.clean_text or None


__all__ = ["TextColumn"]
