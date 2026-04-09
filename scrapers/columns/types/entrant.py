from typing import Any

from scrapers.columns.helpers.link_lookup import build_link_lookup
from scrapers.columns.helpers.results_parsing import ResultsParsingHelpers
from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.helpers.cell_splitting import split_cell_on_br


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

        segments = split_cell_on_br(cell, replace_link_breaks=True)
        link_lookup = build_link_lookup(ctx.links or [])

        entrants: list[dict[str, Any]] = []
        for segment in segments:
            parsed = ResultsParsingHelpers.parse_entrant_segment(
                segment,
                link_lookup,
                ctx.base_url,
            )
            if parsed:
                entrants.append(parsed)

        return entrants


__all__ = ["EntrantColumn"]
