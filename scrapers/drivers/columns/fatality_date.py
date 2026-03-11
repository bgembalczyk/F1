from typing import Any
from typing import Dict

from scrapers.base.helpers.date_parsing import parse_date_with_category_marker
from scrapers.base.helpers.date_parsing import parse_formula_category
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.drivers.constants import MARK_F2_CATEGORY


class FatalityDateColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Dict[str, Any]:
        return {
            "date": parse_date_with_category_marker(ctx, MARK_F2_CATEGORY),
            "formula_category": parse_formula_category(ctx, MARK_F2_CATEGORY),
        }

    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        values = self.parse(ctx)
        for key, value in values.items():
            if ctx.model_fields is not None and key not in ctx.model_fields:
                continue
            record[key] = value
