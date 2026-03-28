from __future__ import annotations

from typing import Generic
from typing import TypeVar

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.contracts import ColumnParseResult
from scrapers.base.table.columns.contracts import LegacyColumnParser
from scrapers.base.table.columns.types.base import BaseColumn

T = TypeVar("T")


class LegacyColumnAdapter(BaseColumn, Generic[T]):
    """Adapter allowing incremental migration from legacy parse() return values."""

    def __init__(self, legacy: LegacyColumnParser[T]) -> None:
        self._legacy = legacy

    def parse(self, ctx: ColumnContext) -> ColumnParseResult | object:
        return self._legacy.parse(ctx)
