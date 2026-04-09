from typing import Any

from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.helpers.parsing import parse_fuel_injection_pressure_limit


class FuelInjectionPressureLimitColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any] | None:
        return parse_fuel_injection_pressure_limit(ctx)


__all__ = ["FuelInjectionPressureLimitColumn"]
