from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


class ConstructorTablesSectionParser:
    def __init__(self, *, section_id: str, section_label: str) -> None:
        self._section_id = section_id
        self._section_label = section_label
        self._tables = ArticleTablesParser()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return SectionParseResult(
            section_id=self._section_id,
            section_label=self._section_label,
            records=self._tables.parse(section_fragment),
            metadata={"parser": self.__class__.__name__},
        )
