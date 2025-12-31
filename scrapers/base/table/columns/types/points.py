from __future__ import annotations

import re

from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn

_FRACTION_RE = re.compile(r"(?:(\d+)\s+)?(\d+)\s*[\/⁄]\s*(\d+)")
_POINTS_WITH_TOTAL_RE = re.compile(r"^(.*?)\(([^)]+)\)")


class PointsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if not text:
            return None

        match = _POINTS_WITH_TOTAL_RE.search(text)
        if match:
            main_text = match.group(1).strip()
            total_text = match.group(2).strip()
            return {
                "championship_points": _parse_points_value(main_text),
                "total_points": _parse_points_value(total_text),
            }

        return _parse_points_value(text)


def _parse_points_value(text: str):
    if not text:
        return None

    match = _FRACTION_RE.search(text)
    if match:
        whole = int(match.group(1)) if match.group(1) else 0
        numerator = int(match.group(2))
        denominator = int(match.group(3))
        if denominator == 0:
            return None
        return whole + numerator / denominator

    return parse_float_from_text(text)
