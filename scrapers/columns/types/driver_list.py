"""Base column rule for driver list parsing."""

from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.helpers.links import normalize_links
from scrapers.helpers.text import strip_marks


class DriverListColumn(BaseColumn):
    """
    Kolumna specjalna dla kierowców, zwraca listę linków [{text, url}, ...].
    Ignoruje flagi (linki z pustym tekstem) i w razie braku linków używa
    czystego tekstu z komórki jako pojedynczej pozycji.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        links = [link for link in normalize_links(ctx.links or []) if link.get("text")]
        if links:
            return links

        if ctx.clean_text:
            text = strip_marks(ctx.clean_text)
            if text:
                return [{"text": text, "url": None}]

        return []


__all__ = ["DriverListColumn"]
