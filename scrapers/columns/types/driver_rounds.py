from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.columns.helpers.driver_parsing import DriverParsingHelpers
from scrapers.columns.helpers.link_lookup import build_link_lookup
from scrapers.helpers.cell_splitting import split_cell_on_br


class DriversWithRoundsColumn(BaseColumn):
    def __init__(self, *, total_rounds: int | None = None) -> None:
        self.total_rounds = total_rounds

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return []

        segments = split_cell_on_br(cell)
        link_lookup = build_link_lookup(ctx.links or [])

        drivers: list[dict[str, Any]] = []
        for segment in segments:
            parsed = DriverParsingHelpers.parse_segment(
                segment,
                link_lookup,
                ctx.base_url,
            )
            if parsed:
                drivers.append(parsed)

        return drivers
