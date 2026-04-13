from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.columns.helpers.constructor_parsing import ConstructorParsingHelpers
from scrapers.columns.helpers.constructor_part_parser import ConstructorPartParserABC


class ConstructorPartColumn(BaseColumn, ConstructorPartParserABC):
    def __init__(self, index: int) -> None:
        self.index = index

    def parse(self, ctx: ColumnContext):
        return ConstructorParsingHelpers.extract_part(ctx, self.index)


__all__ = ["ConstructorPartColumn"]
