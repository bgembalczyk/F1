from typing import Any, Callable, Mapping

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.helpers.text import parse_float_from_text, parse_int_from_text
from scrapers.base.helpers.parsing import parse_float_from_text, parse_int_from_text


@column_type_registry.register("parsed_value")
class ParsedValueColumn(BaseColumn):
    _DEFAULT_PARSERS: Mapping[type, Callable[[str], Any]] = {
        int: parse_int_from_text,
        float: parse_float_from_text,
        str: lambda text: text,
    }

    def __init__(self, target_type: type, parser: Callable[[str], Any] | None = None):
        self._target_type = target_type
        self._parser = parser

    def parse(self, ctx: ColumnContext) -> Any:
        parser = self._parser or self._DEFAULT_PARSERS.get(self._target_type)
        if parser is not None:
            return parser(ctx.clean_text)

        return self._target_type(ctx.clean_text)
