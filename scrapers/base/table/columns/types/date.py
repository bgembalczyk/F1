# scrapers/base/table/columns/types/date.py
from __future__ import annotations

from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.helpers.value_objects import NormalizedDate


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

    Zwraca dict:
        {
            "text": <oryginalny_tekst_bez_refów>,
            "iso": <YYYY-MM-DD | None>,
        }
    """

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return NormalizedDate(text=None, iso=None)

        parsed = parse_date_text(text)
        iso = parsed.get("iso")
        if isinstance(iso, list):
            iso = iso[0] if iso else None

        return NormalizedDate(text=parsed.get("text"), iso=iso)
