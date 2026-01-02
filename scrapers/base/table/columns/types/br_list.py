from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class BrListColumn(BaseColumn):
    """Parses <br>-separated text into a list of cleaned strings."""

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return [ctx.clean_text] if ctx.clean_text else []

        segments = _split_cell_on_br(cell)
        items: list[str] = []
        for segment in segments:
            text = clean_wiki_text(segment.get_text(" ", strip=True))
            if text:
                items.append(text)
        return items


def _split_cell_on_br(cell: Tag) -> list[Tag]:
    html = cell.decode_contents()
    frag_soup = BeautifulSoup(html, "html.parser")
    segments: list[list[Tag]] = [[]]

    for node in list(frag_soup.contents):
        if isinstance(node, Tag) and node.name == "br":
            if segments[-1]:
                segments.append([])
            continue
        segments[-1].append(node)

    wrapped: list[Tag] = []
    for segment in segments:
        if not segment:
            continue
        span = frag_soup.new_tag("span")
        for el in segment:
            span.append(el)
        wrapped.append(span)

    return wrapped or [cell]
