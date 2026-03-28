"""DOMAIN-SPECIFIC: seasons column rule (driver list parsing) localized for seasons domain."""

from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


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
