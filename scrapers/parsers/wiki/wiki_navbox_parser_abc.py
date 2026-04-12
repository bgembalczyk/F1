from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.navbox import WikiNavboxData
from scrapers.parsers.element_parser_abc import NavboxHtmlParserABC


class WikiNavboxParserABC(NavboxHtmlParserABC[WikiNavboxData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiNavboxData: ...


__all__ = ["WikiNavboxParserABC"]
