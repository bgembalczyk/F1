from scrapers.base.table.columns.helpers import extract_constructor_part
from scrapers.base.table.columns.types.func import FuncColumn


class ConstructorPartColumn(FuncColumn):
    def __init__(self, index: int) -> None:
        super().__init__(lambda ctx: extract_constructor_part(ctx, index))
