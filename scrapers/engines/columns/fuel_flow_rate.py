from typing import Any

from scrapers.base.helpers.parsing import parse_fuel_flow_rate
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class FuelFlowRateColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any] | None:
        return parse_fuel_flow_rate(ctx)
