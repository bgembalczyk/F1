# scrapers/base/table/columns/types/auto.py
from typing import Any
import re

from models.records import LinkRecord
from scrapers.base.helpers.text_normalization import clean_text, is_language_link
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class AutoColumn(BaseColumn):
    """
    Zachowanie:
    - domyślnie zwraca tekst z komórki (w tym tekst linków),
    - jeśli jest dokładnie 1 link i cały tekst komórki == tekst linku (po czyszczeniu) → zwraca dict linka,
    - jeśli 1 link + dodatkowy tekst → zwraca tekst,
    - jeśli wiele linków i poza nimi są tylko separatory (',' / ';') → zwraca listę linków,
    - w innym przypadku → zwraca tekst.
    - dodatkowo ignoruje linki „językowe” (es/fr/de/it/...) przy decyzji o zwróceniu dict/listy.
    """

    @staticmethod
    def _normalize_link(link: LinkRecord) -> LinkRecord:
        return {"text": link.get("text") or "", "url": link.get("url")}

    @staticmethod
    def _cell_text(ctx: ColumnContext) -> str:
        if ctx.cell is not None:
            # stripped_strings zachowuje np. "-" jako osobny token
            raw = " ".join(list(ctx.cell.stripped_strings))
            return clean_text(raw)
        return clean_text(ctx.clean_text or getattr(ctx, "raw_text", "") or "")

    def parse(self, ctx: ColumnContext) -> Any:
        value = self._cell_text(ctx)

        # usuń linki “językowe” zanim podejmiesz decyzję o zwróceniu dict-a / listy
        links = [
            self._normalize_link(link)
            for link in (ctx.links or [])
            if not is_language_link(link.get("text"), link.get("url"))
        ]

        # 1) dokładnie jeden sensowny link: dict TYLKO gdy komórka to sam link
        if len(links) == 1:
            link = links[0]
            link_text = clean_text(link.get("text") or "")
            cell_text = clean_text(value or "")
            if cell_text and link_text and cell_text.lower() == link_text.lower():
                return link
            return value or None

        # 2) wiele linków: lista tylko gdy poza linkami są same ',' / ';'
        if len(links) > 1 and ctx.cell is not None:
            raw_html = ctx.cell.decode_contents()
            tmp = raw_html

            for a in ctx.cell.find_all("a", href=True):
                tmp = tmp.replace(str(a), "")

            tmp = re.sub(r"<br\s*/?>", "", tmp, flags=re.IGNORECASE)
            tmp = re.sub(r"\s+|&nbsp;|\xa0", "", tmp)

            if tmp and all(ch in ",;" for ch in tmp):
                return links

        return value or None
