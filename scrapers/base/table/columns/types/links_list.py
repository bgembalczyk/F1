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

    def __init__(self, *, text_for_missing_url: bool = False) -> None:
        super().__init__()
        self.text_for_missing_url = text_for_missing_url

    def parse(self, ctx: ColumnContext) -> Any:
        links = normalize_links(ctx.links or [])
        if not self.text_for_missing_url:
            return links

        return [link["text"] if link.get("url") is None else link for link in links]
