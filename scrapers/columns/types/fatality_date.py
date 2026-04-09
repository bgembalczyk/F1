from typing import Any

from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.constants_drivers import MARK_F2_CATEGORY
from scrapers.helpers.date_parsing import parse_date_with_category_marker
from scrapers.helpers.date_parsing import parse_formula_category


class FatalityDateColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any]:
        return {
            "date": parse_date_with_category_marker(ctx, MARK_F2_CATEGORY),
            "formula_category": parse_formula_category(ctx, MARK_F2_CATEGORY),
        }

    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        values = self.parse(ctx)
        for key, value in values.items():
            if ctx.model_fields is not None and key not in ctx.model_fields:
                continue
            record[key] = value
