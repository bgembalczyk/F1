from typing import Any

from models.records import LinkRecord
from models.validation.validators import normalize_link_record
from scrapers.base.helpers.wiki import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class LinksListColumn(BaseColumn):
    """
    Zwraca ZAWSZE listę linków [{text, url}, ...]
    AUTOMATYCZNE czyszczenie * † ~ ^ itp. z .text
    Wyrzuca linki, które mają pusty tekst.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        cleaned: list[LinkRecord] = []

        for link in ctx.links:
            d: LinkRecord = {"text": link.get("text") or "", "url": link.get("url")}
            text = d.get("text")

            # 1) strip marks
            if isinstance(text, str):
                text = strip_marks(text).strip()
                d["text"] = text

            # 2) skip if no text
            normalized = normalize_link_record(d)
            if not normalized:
                # brak tekstu → NIE dodajemy tego linku do listy
                continue

            cleaned.append(normalized)

        return cleaned
