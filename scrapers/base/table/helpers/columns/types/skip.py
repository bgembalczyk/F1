from typing import Any

from scrapers.base.table.helpers.columns.context import ColumnContext
from scrapers.base.table.helpers.columns.types.base import BaseColumn


class SkipColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.skip_sentinel
