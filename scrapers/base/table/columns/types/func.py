from typing import Callable, Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn


@column_type_registry.register("func")
class FuncColumn(BaseColumn):
    """
    Kolumna bazująca na funkcji: func(ctx) -> value.
    """

    def __init__(self, func: Callable[[ColumnContext], Any]) -> None:
        self.func = func

    def parse(self, ctx: ColumnContext) -> Any:
        return self.func(ctx)
