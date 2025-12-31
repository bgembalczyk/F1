from __future__ import annotations

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class TyreColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if not text:
            return None
        return text[0].upper()
