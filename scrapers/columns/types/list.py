from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.helpers.text_normalization import split_delimited_text


class ListColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.clean_text:
            return []
        return split_delimited_text(ctx.clean_text)


__all__ = ["ListColumn"]
