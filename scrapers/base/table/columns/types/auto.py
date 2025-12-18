# scrapers/base/table/columns/types/auto.py
from typing import Any
import re

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class AutoColumn(BaseColumn):
    """
    Zachowanie:
    - domyślnie zwraca tekst z komórki (w tym tekst linków),
    - jeśli jest dokładnie 1 link i cały tekst komórki == tekst linku (po czyszczeniu) → zwraca dict linka,
    - jeśli 1 link + dodatkowy tekst → zwraca tekst,
    - jeśli wiele linków i poza nimi są tylko separatory (',' / ';') → zwraca listę linków,
    - w innym przypadku (np. "A - B", "A / B", "A (B)") → zwraca tekst.
    """

    _REF_RE = re.compile(r"\[\s*[^]]+\s*]")  # [1], [note 3], [it], ...

    def _clean_text(self, text: str) -> str:
        t = text.replace("\xa0", " ").replace("&nbsp;", " ")
        t = self._REF_RE.sub("", t)
        t = re.sub(r"\s+", " ", t).strip()
        # "Mustang - Yamaha" -> "Mustang-Yamaha"
        t = re.sub(r"\s+[-–]\s+", "-", t)
        return t

    def parse(self, ctx: ColumnContext) -> Any:
        # 1) zawsze buduj "value" z realnej komórki (a nie z ctx.clean_text)
        if ctx.cell is not None:
            raw = ctx.cell.get_text(" ", strip=True)
            value: Any = self._clean_text(raw)
        else:
            value = self._clean_text(ctx.clean_text or "")

        links = ctx.links or []

        # 2) dokładnie jeden link: zwróć dict TYLKO gdy komórka to sam link
        if len(links) == 1:
            link = dict(links[0])
            link_text = self._clean_text(link.get("text") or "")
            cell_text = self._clean_text(value or "")
            if cell_text and link_text and cell_text.lower() == link_text.lower():
                return link
            return value or None

        # 3) wiele linków: lista TYLKO gdy poza linkami są same ',' / ';'
        if len(links) > 1 and ctx.cell is not None:
            raw_html = ctx.cell.decode_contents()

            # usuń wszystkie <a ...>...</a>
            tmp = raw_html
            for a in ctx.cell.find_all("a", href=True):
                tmp = tmp.replace(str(a), "")

            # usuń <br> i whitespace/nbsp
            tmp = re.sub(r"<br\s*/?>", "", tmp, flags=re.IGNORECASE)
            tmp = re.sub(r"\s+|&nbsp;|\xa0", "", tmp)

            # jeśli zostały wyłącznie separatory -> zwróć listę linków
            if tmp and all(ch in ",;" for ch in tmp):
                return links

        # 4) fallback -> tekst
        return value or None
