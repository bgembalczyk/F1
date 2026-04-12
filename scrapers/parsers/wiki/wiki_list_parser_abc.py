from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.list import WikiListData
from scrapers.parsers.element_parser_abc import ListHtmlParserABC


class WikiListParserABC(ListHtmlParserABC[WikiListData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiListData: ...


__all__ = ["WikiListParserABC"]
