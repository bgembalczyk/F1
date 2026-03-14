from typing import Any

from scrapers.base.helpers.parsing import parse_engine_rpm_limit
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class EngineRpmLimitColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any] | None:
        return parse_engine_rpm_limit(ctx)
