from typing import Any

from scrapers.base.helpers.utils import parse_int_from_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class IntColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_int_from_text(ctx.clean_text)
