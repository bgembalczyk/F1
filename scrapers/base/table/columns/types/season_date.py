from __future__ import annotations

import re

from scrapers.base.helpers.time import parse_date_text
from scrapers.base.helpers.value_objects import NormalizedDate
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class SeasonDateColumn(BaseColumn):
    def __init__(self, *, year: int | None) -> None:
        self.year = year

    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if not text:
            return NormalizedDate(text=None, iso=None)

        if self.year and not _has_year(text):
            text = f"{text} {self.year}"

        parsed = parse_date_text(text)
        return NormalizedDate(text=parsed.get("text"), iso=parsed.get("iso"))


def _has_year(text: str) -> bool:
    return re.search(r"\\b\\d{4}\\b", text) is not None
