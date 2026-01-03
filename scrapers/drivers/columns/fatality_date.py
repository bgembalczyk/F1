from typing import Any, Dict

from scrapers.base.helpers.time import parse_date_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.drivers.constants import MARK_F2_CATEGORY


class FatalityDateColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Dict[str, Any]:
        return {
            "date": self._parse_date(ctx),
            "formula_category": self._parse_formula_category(ctx),
        }

    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        values = self.parse(ctx)
        for key, value in values.items():
            if ctx.model_fields is not None and key not in ctx.model_fields:
                continue
            record[key] = value

    @staticmethod
    def _parse_date(ctx: ColumnContext) -> str | None:
        text = (ctx.clean_text or "").replace(MARK_F2_CATEGORY, "").strip()
        if not text:
            return None
        parsed = parse_date_text(text)
        iso = parsed.iso
        if isinstance(iso, list):
            return iso[0] if iso else None
        return iso

    @staticmethod
    def _parse_formula_category(ctx: ColumnContext) -> str | None:
        if not (ctx.raw_text or "").strip():
            return None
        return "F2" if MARK_F2_CATEGORY in (ctx.raw_text or "") else "F1"
