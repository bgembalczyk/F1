from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.columns.types.points import PointsColumn


class PointsOrTextColumn(BaseColumn):
    def __init__(self) -> None:
        self._points = PointsColumn()

    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        parsed = self._points.parse(ctx)
        if parsed is None and text not in {"-", "—"}:
            return text
        return parsed
