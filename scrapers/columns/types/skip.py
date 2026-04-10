from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext


class SkipColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.skip_sentinel


__all__ = ["SkipColumn"]
