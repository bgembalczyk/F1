from typing import Any

from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.helpers.parsing import parse_engine_rpm_limit


class EngineRpmLimitColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any] | None:
        return parse_engine_rpm_limit(ctx)


__all__ = ["EngineRpmLimitColumn"]
