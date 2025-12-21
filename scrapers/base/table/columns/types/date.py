# scrapers/base/table/columns/types/date.py
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Optional, List

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


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

    _RANGE_SPLIT = re.compile(r"\s*[–-]\s*")

    # typowe formaty dat z Wikipedii
    _FORMATS: List[str] = [
        "%d %B %Y",  # 7 June 2019
        "%d %b %Y",  # 7 Jun 2019
        "%B %d, %Y",  # June 7, 2019
        "%b %d, %Y",  # Jun 7, 2019
    ]

    def _clean_base(self, text: str) -> str:
        # obetnij wszystko po nawiasie
        base = text.split("(", 1)[0].strip()
        # jeżeli jest zakres "7–8 June 2019" -> weź pierwszą część
        parts = self._RANGE_SPLIT.split(base)
        if len(parts) > 1:
            # próbujemy zrekonstruować pierwszą datę razem z "resztą"
            # np. "7–8 June 2019" -> pierwsza część: "7", reszta: "June 2019"
            first = parts[0].strip()
            tail = parts[-1].strip()
            if any(ch.isalpha() for ch in tail):
                base = f"{first} {tail}"
            else:
                base = parts[0].strip()
        return base

    def _parse_iso(self, base: str) -> Optional[str]:
        # 1) Format pełny (dzień + miesiąc + rok)
        for fmt in self._FORMATS:
            try:
                dt = datetime.strptime(base, fmt)
                return dt.date().isoformat()  # YYYY-MM-DD
            except ValueError:
                continue

        # 2) Format miesiąc + rok → YYYY-MM
        #    obsługujemy np. "February 2008", "Feb 2008"
        for fmt in ("%B %Y", "%b %Y"):
            try:
                dt = datetime.strptime(base, fmt)
                return dt.strftime("%Y-%m")
            except ValueError:
                continue

        # 3) Sam rok → YYYY
        if re.fullmatch(r"\d{4}", base):
            return base  # bez "-01-01"

        return None

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return {"text": None, "iso": None}

        base = self._clean_base(text)
        if not base:
            return {"text": text, "iso": None}

        iso = self._parse_iso(base)
        return {"text": text, "iso": iso}
