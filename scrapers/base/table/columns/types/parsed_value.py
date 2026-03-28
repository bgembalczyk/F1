from collections.abc import Callable
from collections.abc import Mapping

from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.contracts import ColumnParseResult
from scrapers.base.table.columns.types.base import BaseColumn


class ParsedValueColumn(BaseColumn):
    _DEFAULT_PARSERS: Mapping[type, Callable[[str], object]] = {
        int: parse_int_from_text,
        float: parse_float_from_text,
        str: lambda text: text,
    }

    def __init__(
        self,
        target_type: type,
        parser: Callable[[str], object] | None = None,
    ):
        self._target_type = target_type
        self._parser = parser

    def parse(self, ctx: ColumnContext) -> ColumnParseResult:
        parser = self._parser or self._DEFAULT_PARSERS.get(self._target_type)
        if parser is not None:
            return ColumnParseResult.from_value(parser(ctx.clean_text))

        return ColumnParseResult.from_value(self._target_type(ctx.clean_text))
