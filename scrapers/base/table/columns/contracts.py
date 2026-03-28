from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from typing import TypeVar

from scrapers.base.table.columns.context import ColumnContext

T = TypeVar("T")


@dataclass(frozen=True)
class ColumnParseResult:
    """Unified parse contract for table columns."""

    value: object | None = None
    skip: bool = False

    @classmethod
    def from_value(cls, value: object | None) -> "ColumnParseResult":
        return cls(value=value, skip=False)

    @classmethod
    def skipped(cls) -> "ColumnParseResult":
        return cls(skip=True)


class LegacyColumnParser(Protocol[T]):
    """Legacy parser shape kept for staged migrations."""

    def parse(self, ctx: ColumnContext) -> T: ...


def normalize_column_parse_result(
    result: object,
    *,
    skip_sentinel: object,
) -> ColumnParseResult:
    if isinstance(result, ColumnParseResult):
        return result
    if result is skip_sentinel:
        return ColumnParseResult.skipped()
    return ColumnParseResult.from_value(result)
