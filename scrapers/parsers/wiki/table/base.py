from __future__ import annotations

from abc import ABC
from typing import Any

from bs4 import Tag

from scrapers.parsers.table_parser_abc import TableParserABC


class WikiTableBaseParser(TableParserABC, ABC):
    """Bazowa klasa parserów tabel wiki (HTML Tag -> parsed data)."""

    def parse(self, raw: Tag) -> dict[str, Any]:
        raise NotImplementedError




__all__ = [
    "WikiTableBaseParser",
]
