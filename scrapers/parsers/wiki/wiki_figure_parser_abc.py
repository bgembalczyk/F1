from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import Tag

from models.data.wiki.figure import WikiFigureData
from scrapers.parsers.element_parser_abc import FigureHtmlParserABC


class WikiFigureParserABC(FigureHtmlParserABC[WikiFigureData], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> WikiFigureData: ...


__all__ = ["WikiFigureParserABC"]
