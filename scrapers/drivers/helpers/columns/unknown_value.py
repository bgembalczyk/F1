from __future__ import annotations

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class UnknownValueColumn(BaseColumn):
    def __init__(self, inner: BaseColumn, *, unknown_token: str = "unknown") -> None:
        self.inner = inner
        self.unknown_token = unknown_token

    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if text == "?":
            return self.unknown_token
        return self.inner.parse(ctx)
