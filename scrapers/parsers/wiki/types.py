from __future__ import annotations

from typing import Any
from typing import TypedDict


class WikiFigureData(TypedDict):
    caption: str | None
    src: str | None


class WikiListData(TypedDict):
    items: list[str]


class WikiInfoboxData(TypedDict):
    title: str | None
    rows: dict[str, Any]


class WikiNavboxLinkData(TypedDict):
    text: str | None
    href: str


class WikiNavboxData(TypedDict):
    title: str | None
    links: list[WikiNavboxLinkData]


class WikiTableData(TypedDict):
    headers: list[str]
    rows: list[list[str]]
    raw_rows: list[dict[str, str]]
    rich_rows: list[dict[str, Any]]


class WikiSectionData(TypedDict):
    sections: list[dict[str, Any]]


__all__ = [
    "WikiFigureData",
    "WikiInfoboxData",
    "WikiListData",
    "WikiNavboxData",
    "WikiNavboxLinkData",
    "WikiSectionData",
    "WikiTableData",
]
