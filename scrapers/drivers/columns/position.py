"""DOMAIN-SPECIFIC: drivers column rule (position semantics) localized for drivers domain."""

from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class PositionColumn(BaseColumn):
    TIED = object()

    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if not text or text == "-":
            return None
        if text == "=":
            return self.TIED
        parsed = parse_int_from_text(text)
        if parsed is not None:
            return parsed
        return text
