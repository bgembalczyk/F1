from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


class CircuitEventsSectionParser:
    def __init__(self) -> None:
        self._tables = ArticleTablesParser()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return SectionParseResult(
            section_id="Events",
            section_label="Events",
            records=self._tables.parse(section_fragment),
            metadata={"parser": self.__class__.__name__},
        )
