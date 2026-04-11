from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.helpers.parsing import parse_fuel_flow_rate


class FuelFlowRateColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any] | None:
        return parse_fuel_flow_rate(ctx)


__all__ = ["FuelFlowRateColumn"]
