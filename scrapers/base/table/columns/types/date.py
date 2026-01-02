# scrapers/base/table/columns/types/date.py
from typing import Any

from scrapers.base.helpers.value_objects.normalized_date import NormalizedDate
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.helpers.time import parse_date_text


class DateColumn(BaseColumn):
    """
    Parsuje daty z Wikipedii do formatu ISO (YYYY-MM-DD), jeśli to możliwe.

    Obsługiwane przykłady:
    - "7 June 2019"
    - "7 Jun 2019"
    - "June 7, 2019"
    - "Jun 7, 2019"
    - "7–8 June 2019"  -> bierze pierwszą datę
    - "7 June 2019 (race 1)" -> ignoruje część w nawiasie

    Zwraca NormalizedDate:
        NormalizedDate(text=<oryginalny_tekst_bez_refów>, iso=<YYYY-MM-DD | None>)
    """

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return NormalizedDate(text=None, iso=None)

        parsed = parse_date_text(text)
        return NormalizedDate(text=parsed.get("text"), iso=parsed.get("iso"))
