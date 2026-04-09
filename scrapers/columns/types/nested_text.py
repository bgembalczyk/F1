from typing import Any

from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext


class NestedTextColumn(BaseColumn):
    def __init__(self, subkey: str) -> None:
        self.subkey = subkey

    def parse(self, ctx: ColumnContext) -> str | None:
        text = (ctx.clean_text or "").strip()
        return text or None

    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        if ctx.model_fields is not None and ctx.key not in ctx.model_fields:
            return
        value = self.parse(ctx)
        container = record.setdefault(ctx.key, {})
        container[self.subkey] = value


__all__ = ["NestedTextColumn"]
