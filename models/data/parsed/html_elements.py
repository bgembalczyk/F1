from __future__ import annotations

from typing import Any
from typing import TypedDict

from typing_extensions import NotRequired


class ParagraphElementData(TypedDict):
    text: str


class FigureElementData(TypedDict):
    caption: str | None
    src: str | None


class ListElementData(TypedDict):
    items: list[str]


class InfoboxRowData(TypedDict):
    text: str
    links: NotRequired[list[dict[str, str]]]


class InfoboxElementData(TypedDict):
    title: str | None
    rows: dict[str, Any]


class NavboxLinkData(TypedDict):
    text: str | None
    href: str


class NavboxElementData(TypedDict):
    title: str | None
    links: list[NavboxLinkData]


class TableElementData(TypedDict):
    headers: list[str]
    rows: list[list[str]]
    raw_rows: list[dict[str, str]]
    rich_rows: NotRequired[list[dict[str, Any]]]


class SectionElementData(TypedDict):
    sections: list[dict[str, Any]]
