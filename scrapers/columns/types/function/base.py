from collections.abc import Callable
from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext


class FuncColumn(BaseColumn):
    """
    Kolumna bazująca na funkcji: func(ctx) -> value.
    """

    def __init__(self, func: Callable[[ColumnContext], Any]) -> None:
        self.func = func

    def parse(self, ctx: ColumnContext) -> Any:
        return self.func(ctx)


__all__ = ["FuncColumn"]
