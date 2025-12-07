from typing import Any

from scrapers.base.table.helpers.columns.context import ColumnContext
from scrapers.base.table.helpers.columns.types.base import BaseColumn
from scrapers.base.table.helpers.utils import strip_marks


class LinksListColumn(BaseColumn):
    """
    Zwraca ZAWSZE listę linków [{text, url}, ...]
    AUTOMATYCZNE czyszczenie * † ~ ^ itp. z .text
    Wyrzuca linki, które mają pusty tekst.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        cleaned: list[dict[str, Any]] = []

        for link in ctx.links:
            d = dict(link)
            text = d.get("text")

            # 1) strip marks
            if isinstance(text, str):
                text = strip_marks(text).strip()
                d["text"] = text

            # 2) skip if no text
            if not text:
                # brak tekstu → NIE dodajemy tego linku do listy
                continue

            # 3) ensure url exists
            d.setdefault("url", None)

            cleaned.append(d)

        return cleaned
