# scrapers/base/table/columns/types/auto.py
from typing import Any
import re

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn


@column_type_registry.register("auto")
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

    _REF_RE = re.compile(r"\[\s*[^]]+\s*]")  # [1], [note 3], ...

    # krótkie kody językowe (interwiki / znaczniki języka)
    _LANG_CODES = {
        "en",
        "es",
        "fr",
        "de",
        "it",
        "pt",
        "pl",
        "ru",
        "cs",
        "sk",
        "hu",
        "ro",
        "bg",
        "sr",
        "hr",
        "sl",
        "nl",
        "sv",
        "no",
        "da",
        "fi",
        "el",
        "tr",
        "ar",
        "he",
        "id",
        "ms",
        "th",
        "vi",
        "ja",
        "ko",
        "zh",
        "uk",
        "ca",
        "eu",
        "gl",
    }

    def _is_lang_link(self, link: dict) -> bool:
        txt = (link.get("text") or "").strip().lower()
        url = (link.get("url") or "").strip().lower()
        if not txt or not url:
            return False

        # typowy przypadek: tekst "es" i URL do es.wikipedia.org
        if txt in self._LANG_CODES and f"://{txt}.wikipedia.org/" in url:
            return True

        # czasem interwiki bywa do innej wiki z kodem jako tekst
        if txt in self._LANG_CODES and (
            ".wikipedia.org/" in url or ".wikimedia.org/" in url
        ):
            return True

        return False

    def _clean_text(self, text: str) -> str:
        t = (text or "").replace("\xa0", " ").replace("&nbsp;", " ")
        t = self._REF_RE.sub("", t)
        t = re.sub(r"\s+", " ", t).strip()

        # normalizuj różne myślniki do '-'
        t = t.replace("–", "-").replace("—", "-").replace("−", "-").replace("-", "-")

        # sklej myślnik "A - B" -> "A-B" oraz "A- B" / "A -B"
        t = re.sub(r"(?<=\w)\s*-\s*(?=\w)", "-", t)

        # ⚠️ usuń znacznik językowy TYLKO gdy jest osobnym tokenem na końcu
        # np: "David Salvador (es)" / "David Salvador es" / "Yamaha YZF-R9 ( de )"
        # NIGDY nie tnij końcówek słów typu "...circuit" / "...series" / "...cosworth".
        lang_alt = "|".join(sorted(self._LANG_CODES, key=len, reverse=True))

        while True:
            before = t

            # "(es)" / "( es )" na końcu
            t = re.sub(
                rf"\s*\(\s*(?:{lang_alt})\s*\)\s*$", "", t, flags=re.IGNORECASE
            ).strip()
            # " es" na końcu (musi być poprzedzone co najmniej 1 spacją)
            t = re.sub(rf"\s+(?:{lang_alt})\s*$", "", t, flags=re.IGNORECASE).strip()

            if t == before:
                break

        return t

    def _cell_text(self, ctx: ColumnContext) -> str:
        if ctx.cell is not None:
            # stripped_strings zachowuje np. "-" jako osobny token
            raw = " ".join(list(ctx.cell.stripped_strings))
            return self._clean_text(raw)
        return self._clean_text(ctx.clean_text or getattr(ctx, "raw_text", "") or "")

    def parse(self, ctx: ColumnContext) -> Any:
        value = self._cell_text(ctx)

        # usuń linki “językowe” zanim podejmiesz decyzję o zwróceniu dict-a / listy
        links = [
            dict(link) for link in (ctx.links or []) if not self._is_lang_link(link)
        ]

        # 1) dokładnie jeden sensowny link: dict TYLKO gdy komórka to sam link
        if len(links) == 1:
            link = links[0]
            link_text = self._clean_text(link.get("text") or "")
            cell_text = self._clean_text(value or "")
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
