from typing import Any


from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import build_driver_link_lookup
from scrapers.base.table.columns.helpers import parse_entrant_segment
from scrapers.base.table.columns.helpers import split_entrant_cell_on_br
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

        segments = split_entrant_cell_on_br(cell)
        link_lookup = build_driver_link_lookup(ctx.links or [])

        entrants: list[dict[str, Any]] = []
        for segment in segments:
            parsed = parse_entrant_segment(segment, link_lookup)
            if parsed:
                entrants.append(parsed)

        return entrants
