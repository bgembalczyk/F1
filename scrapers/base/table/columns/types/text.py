from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.contracts import ColumnParseResult
from scrapers.base.table.columns.types.base import BaseColumn


class TextColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> ColumnParseResult:
        return ColumnParseResult.from_value(ctx.clean_text or None)
