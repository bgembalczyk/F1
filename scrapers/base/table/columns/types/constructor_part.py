from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constructor_parsing import extract_constructor_part
from scrapers.base.table.columns.types.base import BaseColumn


class ConstructorPartColumn(BaseColumn):
    def __init__(self, index: int) -> None:
        self.index = index

    def parse(self, ctx: ColumnContext):
        return extract_constructor_part(ctx, self.index)
