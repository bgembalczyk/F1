# scrapers/base/table/columns/types/time.py
import re
from typing import Any

from scrapers.base.helpers.time import parse_time_seconds_from_text
from scrapers.base.helpers.value_objects.normalized_time import NormalizedTime
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constants import RE_COLON
from scrapers.base.table.columns.helpers.constants import RE_MINSEC
from scrapers.base.table.columns.helpers.constants import RE_SECONDS
from scrapers.base.table.columns.types.base import BaseColumn


class TimeColumn(BaseColumn):
    """
    Parsuje czasy okrążeń z typowych formatów Wikipedii do sekund.

    Obsługiwane przykłady:
    - "1:23.456"
    - "2:05.9"
    - "59.876"
    - "1m 23.456s"
    - "1 min 23.4 s"

    Zwraca NormalizedTime:
        NormalizedTime(text=<oryginalny_tekst_bez_refów>, seconds=<float | None>)
    """

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").strip()
        if not text:
            return NormalizedTime(text=None, seconds=None)

        # czasem w polu mogą być dodatki typu "(qualifying)",
        # bierzemy to, co przed nawiasem
        base = text.split("(", 1)[0].strip()

        # 1) format "M:SS(.sss)"
        m = RE_COLON.match(base)
        if m:
            seconds = parse_time_seconds_from_text(f"{m.group('min')}:{m.group('sec')}")
            return NormalizedTime(text=text, seconds=seconds)

        # 2) format "M min SS(.sss)s" / "M m SS.s s"
        m = RE_MINSEC.match(base)
        if m:
            minutes = m.group("min")
            seconds = m.group("sec")
            candidate = f"{minutes}:{seconds}" if minutes else seconds
            return NormalizedTime(
                text=text,
                seconds=parse_time_seconds_from_text(candidate),
            )

        # 3) format tylko z sekundami "SS(.sss)" lub "SS(.sss)s"
        m = RE_SECONDS.match(base)
        if m:
            seconds = parse_time_seconds_from_text(m.group("sec"))
            return NormalizedTime(text=text, seconds=seconds)

        # nie udało się sparsować - zwracamy tylko tekst
        return NormalizedTime(text=text, seconds=None)
