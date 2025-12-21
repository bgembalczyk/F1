from typing import Any

from scrapers.base.helpers.text import parse_seasons
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn


@column_type_registry.register("seasons")
class SeasonsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_seasons(ctx.clean_text)
