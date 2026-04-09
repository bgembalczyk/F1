from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.helpers.parsing import parse_int_from_text


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


__all__ = ["PositionColumn"]
