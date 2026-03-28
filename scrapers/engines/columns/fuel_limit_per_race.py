from typing import Any

from scrapers.base.helpers.parsing import parse_fuel_limit_per_race
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class FuelLimitPerRaceColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any] | None:
        return parse_fuel_limit_per_race(ctx)
