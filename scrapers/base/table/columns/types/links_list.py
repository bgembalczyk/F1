from typing import Any, Iterable, Iterator

from bs4 import NavigableString, Tag

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.helpers.wiki import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class LinksListColumn(BaseColumn):
    """
    Zwraca ZAWSZE listę linków [{text, url}, ...]
    AUTOMATYCZNE czyszczenie * † ~ ^ itp. z .text
    Wyrzuca linki, które mają pusty tekst.
    """

    def __init__(self, *, text_for_missing_url: bool = False) -> None:
        super().__init__()
        self.text_for_missing_url = text_for_missing_url
        self._separator_token = object()

    def _clean_text_item(self, text: str) -> str | None:
        cleaned = clean_wiki_text(text)
        cleaned = strip_marks(cleaned or "") or ""
        return cleaned or None

    def _split_text_tokens(self, text: str) -> Iterable[str | object]:
        for index, chunk in enumerate(text.split(",")):
            if index > 0:
                yield self._separator_token
            yield chunk

    def _iter_cell_tokens(
        self,
        cell: Tag,
        *,
        link_iter: Iterator[dict[str, Any]],
    ) -> Iterable[str | dict[str, Any] | object]:
        for child in cell.children:
            if isinstance(child, NavigableString):
                yield from self._split_text_tokens(str(child))
                continue

            if not isinstance(child, Tag):
                continue

            if child.name == "br":
                yield self._separator_token
                continue

            if child.name == "a":
                link = next(link_iter, None)
                if link is not None:
                    yield link
                continue

            yield from self._iter_cell_tokens(child, link_iter=link_iter)

    def parse(self, ctx: ColumnContext) -> Any:
        links = normalize_links(ctx.links or [])
        if not self.text_for_missing_url:
            return links

        if ctx.cell is None:
            if links:
                return [
                    link["text"] if link.get("url") is None else link for link in links
                ]
            text_value = self._clean_text_item(ctx.clean_text)
            return [text_value] if text_value else []

        raw_links = list(ctx.links or [])
        link_iter = iter(raw_links)
        items: list[Any] = []
        text_parts: list[str] = []

        def flush_text_parts() -> None:
            if not text_parts:
                return
            text_value = self._clean_text_item(" ".join(text_parts))
            text_parts.clear()
            if text_value:
                items.append(text_value)

        for token in self._iter_cell_tokens(ctx.cell, link_iter=link_iter):
            if token is self._separator_token:
                flush_text_parts()
                continue

            if isinstance(token, dict):
                flush_text_parts()
                normalized = normalize_links(token)
                if not normalized:
                    continue
                link = normalized[0]
                items.append(link["text"] if link.get("url") is None else link)
                continue

            text_parts.append(str(token))

        flush_text_parts()
        return items
