from typing import Any


from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import split_cell_on_br
from scrapers.base.table.columns.types.base import BaseColumn


class BrListColumn(BaseColumn):
    """Parses <br>-separated text into a list of cleaned strings."""

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return [ctx.clean_text] if ctx.clean_text else []

        segments = split_cell_on_br(cell)
        items: list[str] = []
        for segment in segments:
            text = clean_wiki_text(segment.get_text(" ", strip=True))
            if text:
                items.append(text)
        return items
