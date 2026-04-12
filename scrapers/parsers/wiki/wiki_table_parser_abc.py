from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.table import WikiTableData
from scrapers.parsers.wiki.wiki_list_parser_abc import WikiListParserABC


class WikiTableParserABC(WikiListParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiTableData: ...


__all__ = ["WikiTableParserABC"]
