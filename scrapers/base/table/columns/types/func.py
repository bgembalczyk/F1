from collections.abc import Callable
from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.constants import SKIP_SENTINEL


class FuncColumn(BaseColumn):
    """
    Kolumna bazująca na funkcji: func(ctx) -> value.
    """

    _skip = SKIP_SENTINEL

    def __init__(self, func: Callable[[ColumnContext], Any]) -> None:
        self.func = func

    def parse(self, ctx: ColumnContext) -> Any:
        return self.func(ctx)
