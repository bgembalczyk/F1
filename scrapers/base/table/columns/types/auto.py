# scrapers/base/table/columns/types/auto.py
import re

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class AutoColumn(BaseColumn):
    """
    Zachowanie:
    - domyślnie zwraca tekst z komórki (w tym tekst linków),
    - jeśli jest dokładnie 1 link i cały tekst komórki == tekst linku
      (po czyszczeniu) -> zwraca dict linka,
    - jeśli 1 link + dodatkowy tekst -> zwraca tekst,
    - jeśli wiele linków i poza nimi są tylko separatory (',' / ';')
      -> zwraca listę linków,
    - w innym przypadku -> zwraca tekst.
    - dodatkowo ignoruje linki "językowe" (es/fr/de/it/...)
      przy decyzji o zwróceniu dict/listy.
    """

    def __init__(
        self,
        *,
        strip_lang_suffix: bool = True,
        strip_refs: bool = True,
        normalize_dashes: bool = True,
    ) -> None:
        self.strip_lang_suffix = strip_lang_suffix
        self.strip_refs = strip_refs
        self.normalize_dashes = normalize_dashes

    def _cell_text(self, ctx: ColumnContext) -> str:
        if ctx.cell is not None:
            # stripped_strings zachowuje np. "-" jako osobny token
            raw = " ".join(list(ctx.cell.stripped_strings))
            return clean_wiki_text(
                raw,
                strip_lang_suffix=self.strip_lang_suffix,
                strip_refs=self.strip_refs,
                normalize_dashes=self.normalize_dashes,
            )
        return clean_wiki_text(
            ctx.clean_text or getattr(ctx, "raw_text", "") or "",
            strip_lang_suffix=self.strip_lang_suffix,
            strip_refs=self.strip_refs,
            normalize_dashes=self.normalize_dashes,
        )

    def parse(self, ctx: ColumnContext) -> object:
        value = self._cell_text(ctx)

        # usuń linki “językowe” zanim podejmiesz decyzję o zwróceniu dict-a / listy
        links = normalize_links(
            ctx.links or [],
            strip_marks=False,
            drop_empty=True,
            strip_lang_suffix=self.strip_lang_suffix,
        )

        # 1) dokładnie jeden sensowny link: dict TYLKO gdy komórka to sam link
        if len(links) == 1:
            link = links[0]
            link_text = clean_wiki_text(
                link.get("text") or "",
                strip_lang_suffix=self.strip_lang_suffix,
                strip_refs=self.strip_refs,
                normalize_dashes=self.normalize_dashes,
            )
            cell_text = clean_wiki_text(
                value or "",
                strip_lang_suffix=self.strip_lang_suffix,
                strip_refs=self.strip_refs,
                normalize_dashes=self.normalize_dashes,
            )
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
