from __future__ import annotations

import re
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
    parts = re.split(r"<br\\s*/?>", html, flags=re.IGNORECASE)
    segments: list[Tag] = []
    soup = cell.soup or BeautifulSoup("", "html.parser")

    for part in parts:
        if not part.strip():
            continue
        frag_soup = BeautifulSoup(part, "html.parser")
        span = soup.new_tag("span")
        for el in list(frag_soup.contents):
            span.append(el)
        segments.append(span)

    return segments or [cell]
