from models.value_objects.date.normalized import NormalizedDate
from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.columns.helpers.results_parsing import ResultsParsingHelpers
from scrapers.helpers.time import parse_date_text


class SeasonDateColumn(BaseColumn):
    def __init__(self, *, year: int | None) -> None:
        self.year = year

    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if not text:
            return NormalizedDate(text=None, iso=None)

        if self.year and not ResultsParsingHelpers.has_year(text):
            text = f"{text} {self.year}"

        parsed = parse_date_text(text)
        return NormalizedDate(text=parsed.raw, iso=parsed.iso)
