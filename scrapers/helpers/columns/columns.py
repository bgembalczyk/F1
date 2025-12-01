from abc import ABC, abstractmethod
from typing import Any, List, Dict, Callable

from scrapers.helpers.columns.column_context import ColumnContext
from scrapers.helpers.f1_table_utils import clean_wiki_text, parse_seasons, extract_links_from_cell, \
    parse_int_from_text, parse_float_from_text


# ==========================
#  BAZOWA KOLUMNA
# ==========================

class BaseColumn(ABC):
    """
    Bazowa klasa dla wszystkich typów kolumn.

    Domyślnie:
    - parse() zwraca wartość,
    - apply() zapisuje ją pod ctx.key w rekordzie,
      chyba że wartość == ctx.skip_sentinel.
    """

    @abstractmethod
    def parse(self, ctx: ColumnContext) -> Any:
        """
        Zwraca sparsowaną wartość dla danej komórki.
        """
        raise NotImplementedError

    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        value = self.parse(ctx)
        if value is ctx.skip_sentinel:
            return
        record[ctx.key] = value


class FuncColumn(BaseColumn):
    """
    Kolumna bazująca na funkcji: func(ctx) -> value.
    """

    def __init__(self, func: Callable[[ColumnContext], Any]) -> None:
        self.func = func

    def parse(self, ctx: ColumnContext) -> Any:
        return self.func(ctx)


class MultiColumn(BaseColumn):
    """
    Kompozycyjny MultiColumn: jedna komórka -> wiele pól w rekordzie.

    Przykład:
        MultiColumn({
            "circuit": UrlColumn(),
            "circuit_status": EnumColumn(mapping),
        })
    """

    def __init__(self, subcolumns: Dict[str, BaseColumn]) -> None:
        self.subcolumns = subcolumns

    def parse(self, ctx: ColumnContext) -> Any:
        # opcjonalnie – zwraca dict; niekoniecznie używane
        result: Dict[str, Any] = {}
        for new_key, col in self.subcolumns.items():
            subctx = ColumnContext(
                header=ctx.header,
                key=new_key,
                raw_text=ctx.raw_text,
                clean_text=ctx.clean_text,
                links=ctx.links,
                cell=ctx.cell,
                skip_sentinel=ctx.skip_sentinel,
            )
            val = col.parse(subctx)
            if val is not ctx.skip_sentinel:
                result[new_key] = val
        return result

    def apply(self, ctx: ColumnContext, record: Dict[str, Any]) -> None:
        for new_key, col in self.subcolumns.items():
            subctx = ColumnContext(
                header=ctx.header,
                key=new_key,
                raw_text=ctx.raw_text,
                clean_text=ctx.clean_text,
                links=ctx.links,
                cell=ctx.cell,
                skip_sentinel=ctx.skip_sentinel,
            )
            col.apply(subctx, record)


# ==========================
#  PROSTE KOLUMNY
# ==========================

class SkipColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.skip_sentinel


class AutoColumn(BaseColumn):
    """
    Domyślne zachowanie:
    - clean_text,
    - jeśli jest dokładnie 1 link → dict{text, url},
    - jeśli wiele linków i tylko przecinki między nimi → lista linków.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        value: Any = ctx.clean_text

        links = ctx.links
        if len(links) == 1:
            return links[0]

        if len(links) > 1:
            # spróbuj wykryć przypadek "link, link, link"
            import re

            raw_html = "".join(str(x) for x in ctx.cell.contents)
            cleaned_html = re.sub(r"\s+|&nbsp;|\xa0", "", raw_html)
            tmp = cleaned_html
            for a in ctx.cell.find_all("a", href=True):
                link_html = re.sub(r"\s+|&nbsp;|\xa0", "", str(a))
                tmp = tmp.replace(link_html, "")

            if all(ch == "," for ch in tmp if ch != ""):
                return links

        return value


class TextColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.clean_text or None


class ListColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        if not ctx.clean_text:
            return []
        parts = [p.strip() for p in ctx.clean_text.split(",") if p.strip()]
        return parts


class SeasonsColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_seasons(ctx.clean_text)


class IntColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_int_from_text(ctx.clean_text)


class FloatColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        return parse_float_from_text(ctx.clean_text)


class SingleLinkColumn(BaseColumn):
    """
    Zwraca pierwszy link ({text, url}) lub None.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.links[0] if ctx.links else None


class LinksListColumn(BaseColumn):
    """
    Zawsze lista linków (lista {text, url}).
    """

    def parse(self, ctx: ColumnContext) -> Any:
        return ctx.links


class EnumMarksColumn(BaseColumn):
    """
    Ogólny enum_column dla znaków (np. *, †) w raw_text.

    mapping: znak -> wartość enum
    default: wartość gdy żaden znak nie pasuje
    """

    def __init__(self, mapping: Dict[str, Any], default: Any = None) -> None:
        self.mapping = dict(mapping)
        self.default = default

    def parse(self, ctx: ColumnContext) -> Any:
        text = ctx.raw_text or ""
        for mark, value in self.mapping.items():
            if mark in text:
                return value
        return self.default