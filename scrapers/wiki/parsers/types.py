from __future__ import annotations

from typing import Any
from typing import TypedDict

from typing_extensions import NotRequired

WikiParserData = dict[str, Any]


class WikiParsedPayload(TypedDict):
    """Wspólny payload zwracany przez parsery elementów wiki."""

    kind: str
    source_section_id: str | None
    confidence: float
    raw_html_fragment: str
    data: WikiParserData
    # legacy compatibility:
    type: str


class HeaderParsedData(TypedDict):
    title: str | None


class CategoryLinkItem(TypedDict):
    text: str
    href: str


class CategoryGroup(TypedDict):
    category: str | None
    links: list[CategoryLinkItem]


class CategoryLinksParsedData(TypedDict):
    categories: list[CategoryGroup]


class ParagraphParsedData(TypedDict):
    text: str


class FigureParsedData(TypedDict):
    caption: str | None
    src: str | None


class ListParsedData(TypedDict):
    items: list[str]


class NavBoxParsedData(TypedDict):
    title: str | None
    links: list[CategoryLinkItem]


class ReferencesWrapParsedData(TypedDict):
    references: list[str]


class InfoboxParsedData(TypedDict):
    title: str | None
    rows: dict[str, Any]


class RichCellData(TypedDict):
    text: str
    links: list[dict[str, Any]]
    background: str | None


class TableParsedData(TypedDict):
    headers: list[str]
    rows: list[list[str]]
    raw_rows: list[dict[str, str]]
    rich_rows: NotRequired[list[dict[str, Any]]]
