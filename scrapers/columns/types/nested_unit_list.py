import re
from typing import Any

from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.constants.patterns import UNIT_RE
from scrapers.helpers.parsing import parse_numeric_value
from scrapers.parsers.helpers import normalize_unit
from scrapers.parsers.helpers import parse_unit_list
from scrapers.parsers.unit_value import UnitValue


class NestedUnitListColumn(BaseColumn):
    def __init__(self, subkey: str) -> None:
        self.subkey = subkey

    def _parse_min_max(self, text: str) -> dict[str, UnitValue] | list[UnitValue]:
        values = parse_unit_list(text)
        if not values:
            return []

        min_value = None
        max_value = None
        for match in UNIT_RE.finditer(text):
            value = parse_numeric_value(match.group("value"))
            unit = normalize_unit(match.group("unit"))
            suffix = text[match.end() : match.end() + 12].lower()
            if "min" in suffix:
                min_value = {"value": value, "unit": unit}
            elif max_value is None:
                max_value = {"value": value, "unit": unit}

        if min_value is None:
            return values
        if max_value is None and values:
            max_value = values[0]
        return {"max": max_value, "min": min_value}

    def parse(self, ctx: ColumnContext) -> Any:
        text = ctx.clean_text or ""
        if not text:
            return []
        if re.search(r"\bprohibited\b", text, flags=re.IGNORECASE):
            return "prohibited"
        if re.search(r"\bmin\.?\b", text, flags=re.IGNORECASE):
            return self._parse_min_max(text)
        return parse_unit_list(text)

    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        if ctx.model_fields is not None and ctx.key not in ctx.model_fields:
            return
        value = self.parse(ctx)
        container = record.setdefault(ctx.key, {})
        container[self.subkey] = value


__all__ = ["NestedUnitListColumn"]
