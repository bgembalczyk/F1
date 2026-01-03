from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import has_year
from scrapers.base.table.columns.types.base import BaseColumn


class SeasonDateColumn(BaseColumn):
    def __init__(self, *, year: int | None) -> None:
        self.year = year

    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if not text:
            return NormalizedDate(text=None, iso=None)

        if self.year and not has_year(text):
            text = f"{text} {self.year}"

        parsed = parse_date_text(text)
        return NormalizedDate(text=parsed.raw, iso=parsed.iso)
