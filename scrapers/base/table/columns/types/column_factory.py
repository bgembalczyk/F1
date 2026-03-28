from collections.abc import Callable
from typing import Any

from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn


class ColumnFactory:
    """Factory for creating parsed-value columns from types or parser functions."""

    def parse_with(self, type_or_func: type[Any] | Callable[[str], Any]) -> ParsedValueColumn:
        if isinstance(type_or_func, type):
            return ParsedValueColumn(type_or_func)

        return ParsedValueColumn(str, parser=type_or_func)


column_factory = ColumnFactory()


def IntColumn() -> ParsedValueColumn:  # noqa: N802
    """Compatibility layer alias for integer parsing columns."""

    return column_factory.parse_with(int)


def FloatColumn() -> ParsedValueColumn:  # noqa: N802
    """Compatibility layer alias for float parsing columns."""

    return column_factory.parse_with(float)
