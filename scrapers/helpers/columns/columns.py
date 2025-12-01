from abc import ABC, abstractmethod
from typing import Any, List, Dict

from scrapers.helpers.columns.column_context import ColumnContext
from scrapers.helpers.f1_table_utils import clean_wiki_text, parse_seasons, extract_links_from_cell, \
    parse_int_from_text, parse_float_from_text


# ==========================
#  BAZOWA KOLUMNA
# ==========================

class BaseColumn(ABC):
    """
    Bazowa klasa dla wszystkich typów kolumn.
    """

    @abstractmethod
    def parse(self, ctx: ColumnContext) -> Any:
        """
        Zwraca sparsowaną wartość dla danej komórki.
        """
        raise NotImplementedError


# ==========================
#  KONKRETNE TYPY KOLUMN
# ==========================

class AutoColumn(BaseColumn):
    """
    Domyślne zachowanie:
    - tekst wyczyszczony,
    - jeśli include_urls:
        * 1 link → dict{text, url}
        * wiele linków i tylko przecinki między nimi → lista dictów
    """

    def parse(self, ctx: ColumnContext) -> Any:
        value: Any = ctx.clean_text

        if not ctx.include_urls:
            return value

        links = [a for a in ctx.cell.find_all("a", href=True)]
        if len(links) == 1:
            a = links[0]
            href = a.get("href")
            url = ctx.full_url(href)
            if url:
                return {
                    "text": ctx.clean_text,
                    "url": url,
                }

        if len(links) > 1:
            raw_html = "".join(str(x) for x in ctx.cell.contents)

            # prosta heurystyka: jeśli w komórce są tylko linki i przecinki → lista linków
            import re

            cleaned_html = re.sub(r"\s+|&nbsp;|\xa0", "", raw_html)
            tmp = cleaned_html
            for a in links:
                link_html = re.sub(r"\s+|&nbsp;|\xa0", "", str(a))
                tmp = tmp.replace(link_html, "")

            if all(ch == "," for ch in tmp if ch != ""):
                result: List[Dict[str, Any]] = []
                for a in links:
                    t = clean_wiki_text(a.get_text(" ", strip=True))
                    href = a.get("href")
                    url = ctx.full_url(href)
                    result.append({"text": t, "url": url})
                return result

        return value


class SkipColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.skip_sentinel


class TextColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.clean_text or None


class ListColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        base = ctx.clean_text
        if not base:
            return []
        parts = [p.strip() for p in base.split(",") if p.strip()]
        return parts


class SeasonsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_seasons(ctx.clean_text)


class LinkColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        links = extract_links_from_cell(ctx.cell, full_url=ctx.full_url)
        if not links:
            return None
        return links[0]


class ListOfLinksColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return extract_links_from_cell(ctx.cell, full_url=ctx.full_url)


class IntColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_int_from_text(ctx.clean_text)


class FloatColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_float_from_text(ctx.clean_text)
