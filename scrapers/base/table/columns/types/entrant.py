from typing import Any

from scrapers.base.helpers.cell_splitting import split_cell_on_br
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.driver_parsing import DriverParsingHelpers
from scrapers.base.table.columns.helpers.results_parsing import ResultsParsingHelpers
from scrapers.base.table.columns.types.base import BaseColumn


class EntrantColumn(BaseColumn):
    """
    Parses entrant cells into a list of entries, one per <br> row.

    Each entry includes the full name text (without flags), a list of
    title sponsor links found in that row, and the license extracted
    from flag icons.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return []

        segments = split_cell_on_br(cell)
        link_lookup = DriverParsingHelpers.build_link_lookup(ctx.links or [])

        entrants: list[dict[str, Any]] = []
        for segment in segments:
            parsed = ResultsParsingHelpers.parse_entrant_segment(segment, link_lookup, ctx.base_url)
            if parsed:
                entrants.append(parsed)

        return entrants
