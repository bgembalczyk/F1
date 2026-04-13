from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

if TYPE_CHECKING:
    from scrapers.input_types import WikiDictFragmentInput
    from scrapers.input_types import WikiParserInput
    from scrapers.input_types import WikiSoupInput
    from scrapers.input_types import WikiTagInput


def as_tag(value: WikiParserInput) -> WikiTagInput:
    if isinstance(value, Tag):
        return value
    if isinstance(value, dict):
        table = value.get("_table")
        if isinstance(table, Tag):
            return table
    msg = f"Cannot adapt {type(value).__name__} to Tag."
    raise TypeError(msg)


def as_soup(value: WikiParserInput) -> WikiSoupInput:
    if isinstance(value, BeautifulSoup):
        return value
    if isinstance(value, Tag):
        return BeautifulSoup(str(value), "html.parser")
    msg = f"Cannot adapt {type(value).__name__} to BeautifulSoup."
    raise TypeError(msg)


def as_dict_fragment(value: WikiParserInput) -> WikiDictFragmentInput:
    if isinstance(value, dict):
        return value
    if isinstance(value, Tag):
        return {"_table": value}
    msg = f"Cannot adapt {type(value).__name__} to dict fragment."
    raise TypeError(msg)


def as_table_fragments(value: WikiParserInput) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        tables = value.get("tables")
        if isinstance(tables, list):
            return [item for item in tables if isinstance(item, dict)]
        return [value]
    return []


__all__ = [
    "as_dict_fragment",
    "as_soup",
    "as_table_fragments",
    "as_tag",
]
