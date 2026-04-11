from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.columns.types.mixins.enum import EnumMarksMixin
from scrapers.constants_drivers import MARK_F2_CATEGORY
from scrapers.helpers.date_parsing import parse_date_with_category_marker


class FatalityDateColumn(EnumMarksMixin, BaseColumn):
    def __init__(self) -> None:
        super().__init__(mapping={MARK_F2_CATEGORY: "F2"}, default="F1")

    def parse(self, ctx: ColumnContext) -> dict[str, Any]:
        return {
            "date": parse_date_with_category_marker(ctx, MARK_F2_CATEGORY),
            "formula_category": EnumMarksMixin.parse(self, ctx),
        }

    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        values = self.parse(ctx)
        for key, value in values.items():
            if ctx.model_fields is not None and key not in ctx.model_fields:
                continue
            record[key] = value
