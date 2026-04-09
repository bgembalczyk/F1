from typing import Any

from scrapers.columns.types.base import BaseColumn
from scrapers.columns.types.context import ColumnContext
from scrapers.helpers.links import normalize_links


class UrlColumn(BaseColumn):
    """
    Zwraca pierwszy link ({text, url}) albo None.
    AUTOMATYCZNE czyszczenie * † z .text
    """

    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.links:
            normalized = normalize_links(
                [{"text": ctx.clean_text or "", "url": None}],
                strip_lang_suffix=False,
            )
            return normalized[0] if normalized else None

        normalized = normalize_links(ctx.links)
        return normalized[0] if normalized else None


__all__ = ["UrlColumn"]
