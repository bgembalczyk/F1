from typing import Any, Dict

from scrapers.base.helpers.time import parse_date_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


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
        text = (ctx.clean_text or "").replace("#", "").strip()
        if not text:
            return None
        parsed = parse_date_text(text)
        return parsed.get("iso")

    @staticmethod
    def _parse_formula_category(ctx: ColumnContext) -> str | None:
        if not (ctx.raw_text or "").strip():
            return None
        return "F2" if "#" in (ctx.raw_text or "") else "F1"
