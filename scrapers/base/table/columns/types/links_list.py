from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class LinksListColumn(BaseColumn):
    """
    Zwraca ZAWSZE listę linków [{text, url}, ...]
    AUTOMATYCZNE czyszczenie * † ~ ^ itp. z .text
    Wyrzuca linki, które mają pusty tekst.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        return normalize_links(ctx.links or [])
