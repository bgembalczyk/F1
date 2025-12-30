import re
from typing import Callable, Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class UnitColumn(BaseColumn):
    """
    Kolumna parsująca wartość liczbową wraz z jednostką.

    Zwraca dict: {"value": число, "unit": строка}.
    """

    def __init__(
        self,
        unit: str | None = None,
        *,
        value_type: type = float,
        normalize_unit: Callable[[str], str] | None = None,
    ) -> None:
        self.unit = unit
        self.value_type = value_type
        self.normalize_unit = normalize_unit or (lambda u: u)

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").replace("\xa0", " ")
        if not text:
            return None

        if self.unit:
            unit_pattern = re.escape(self.unit)
            match = re.search(
                rf"([-+]?\d[\d,]*(?:\.\d+)?)\s*[-–−]?\s*{unit_pattern}\b",
                text,
                flags=re.IGNORECASE,
            )
            if not match:
                return None
            raw_value = match.group(1)
            unit = self.unit
        else:
            match = re.search(
                r"([-+]?\d[\d,]*(?:\.\d+)?)\s*[-–−]?\s*([A-Za-z][A-Za-z0-9/%]+)",
                text,
            )
            if not match:
                return None
            raw_value = match.group(1)
            unit = match.group(2)

        value = self._cast_number(raw_value)
        normalized_unit = self.normalize_unit(str(unit).strip())
        return {"value": value, "unit": normalized_unit}

    def _cast_number(self, raw: str) -> Any:
        cleaned = raw.replace(",", "")
        try:
            if self.value_type is int:
                return int(float(cleaned))
            return self.value_type(cleaned)
        except (TypeError, ValueError):
            return None
