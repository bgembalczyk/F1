from typing import Any

from scrapers.base.table.helpers.columns.context import ColumnContext
from scrapers.base.table.helpers.columns.types.base import BaseColumn
from scrapers.base.table.helpers.utils import parse_float_from_text


class FloatColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_float_from_text(ctx.clean_text)
