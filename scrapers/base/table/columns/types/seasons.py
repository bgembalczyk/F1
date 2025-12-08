from typing import Any

from scrapers.base.helpers.utils import parse_seasons
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class SeasonsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_seasons(ctx.clean_text)
