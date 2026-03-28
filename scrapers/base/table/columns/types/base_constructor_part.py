from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constructor_parsing import (
    ConstructorParsingHelpers,
)
from scrapers.base.table.columns.types.base import BaseColumn


class BaseConstructorPartColumn(BaseColumn):
    def __init__(self, index: int) -> None:
        self.index = index

    def parse(self, ctx: ColumnContext):
        return ConstructorParsingHelpers.extract_part(ctx, self.index)
