from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.infobox import WikiInfoboxData
from scrapers.parsers.wiki.wiki_list_parser_abc import WikiListParserABC


class WikiInfoboxParserABC(WikiListParserABC, ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiInfoboxData: ...


__all__ = ["WikiInfoboxParserABC"]
