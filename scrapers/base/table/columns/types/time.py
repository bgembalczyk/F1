# scrapers/base/table/columns/types/time.py
from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional

from scrapers.base.helpers.value_objects import NormalizedTime
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn


@column_type_registry.register("time")
class TimeColumn(BaseColumn):
    """
    Parsuje czasy okrążeń z typowych formatów Wikipedii do sekund.

    Obsługiwane przykłady:
    - "1:23.456"
    - "2:05.9"
    - "59.876"
    - "1m 23.456s"
    - "1 min 23.4 s"

    Zwraca dict:
        {
            "text": <oryginalny_tekst_bez_refów>,
            "seconds": <float | None>,
        }
    """

    _RE_COLON = re.compile(r"^\s*(?P<min>\d+)\s*:\s*(?P<sec>\d+(?:\.\d+)?)\s*$")
    _RE_MINSEC = re.compile(
        r"^\s*(?:(?P<min>\d+)\s*(?:m|min|minute(?:s)?)\s*)?"
        r"(?P<sec>\d+(?:\.\d+)?)\s*(?:s|sec|second(?:s)?)\s*$",
        re.IGNORECASE,
    )
    _RE_SECONDS = re.compile(
        r"^\s*(?P<sec>\d+(?:\.\d+)?)\s*(?:s|sec|second(?:s)?)?\s*$",
        re.IGNORECASE,
    )

    def _to_seconds(self, minutes: Optional[str], seconds: str) -> float:
        """
        Parsuje sekundy z zachowaniem precyzji jak w oryginalnym stringu.

        Przykład:
        "1:16.0357" -> 76.0357 (a nie 76.03569999999999)
        """
        m = int(minutes) if minutes is not None else 0

        # używamy Decimal, żeby uniknąć błędów binarnego float
        sec_dec = Decimal(seconds)

        total = Decimal(m * 60) + sec_dec

        # jeżeli mamy część dziesiętną, zaokrąglamy do tej samej liczby miejsc
        if "." in seconds:
            places = len(seconds.split(".", 1)[1])
            quant = Decimal("1." + ("0" * places))
            total = total.quantize(quant, rounding=ROUND_HALF_UP)

        return float(total)

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return NormalizedTime(text=None, seconds=None)

        # czasem w polu mogą być dodatki typu "(qualifying)", bierzemy to, co przed nawiasem
        base = text.split("(", 1)[0].strip()

        # 1) format "M:SS(.sss)"
        m = self._RE_COLON.match(base)
        if m:
            seconds = self._to_seconds(m.group("min"), m.group("sec"))
            return NormalizedTime(text=text, seconds=seconds)

        # 2) format "M min SS(.sss)s" / "M m SS.s s"
        m = self._RE_MINSEC.match(base)
        if m:
            seconds = self._to_seconds(m.group("min"), m.group("sec"))
            return NormalizedTime(text=text, seconds=seconds)

        # 3) format tylko z sekundami "SS(.sss)" lub "SS(.sss)s"
        m = self._RE_SECONDS.match(base)
        if m:
            seconds = self._to_seconds(None, m.group("sec"))
            return NormalizedTime(text=text, seconds=seconds)

        # nie udało się sparsować – zwracamy tylko tekst
        return NormalizedTime(text=text, seconds=None)
