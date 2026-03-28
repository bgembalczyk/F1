from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types import LinksListColumn


class AppendLinksColumn(LinksListColumn):
    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        value = self.parse(ctx)
        if value is ctx.skip_sentinel:
            return
        if ctx.model_fields is not None and ctx.key not in ctx.model_fields:
            return
        if not value:
            return
        record.setdefault(ctx.key, []).extend(value)
