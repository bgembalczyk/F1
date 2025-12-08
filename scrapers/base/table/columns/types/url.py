from typing import Any

from scrapers.base.helpers.utils import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class UrlColumn(BaseColumn):
    """
    Zwraca pierwszy link ({text, url}) albo None.
    AUTOMATYCZNE czyszczenie * † z .text
    """

    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.links:
            if ctx.clean_text:
                return {"text": strip_marks(ctx.clean_text), "url": None}
            return None

        link = dict(ctx.links[0])
        link["text"] = strip_marks(link.get("text"))
        return link
