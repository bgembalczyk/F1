from collections.abc import Callable

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.contracts import ColumnParseResult
from scrapers.base.table.columns.types.base import BaseColumn


class FuncColumn(BaseColumn):
    """
    Kolumna bazująca na funkcji: func(ctx) -> value.
    """

    def __init__(
        self,
        func: Callable[[ColumnContext], ColumnParseResult | object],
    ) -> None:
        self.func = func

    def parse(self, ctx: ColumnContext) -> ColumnParseResult | object:
        return self.func(ctx)
