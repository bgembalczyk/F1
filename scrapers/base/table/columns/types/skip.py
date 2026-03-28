from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.contracts import ColumnParseResult
from scrapers.base.table.columns.types.base import BaseColumn


class SkipColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> ColumnParseResult:
        return ColumnParseResult.skipped()
