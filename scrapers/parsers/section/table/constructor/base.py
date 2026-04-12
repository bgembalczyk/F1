from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.parsers.wiki.base_section_parser import BaseSectionParser
from scrapers.parsers.wiki.table.article import ArticleTablesParser
from scrapers.parsers.wiki.table.contracts import ArticleTablesParserABC
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_metadata


class ConstructorTablesSectionParser(BaseSectionParser):
    def __init__(self, *, section_id: str, section_label: str) -> None:
        self._section_id = section_id
        self._section_label = section_label
        self._tables: ArticleTablesParserABC = ArticleTablesParser()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        return SectionParseResult(
            section_id=self._section_id,
            section_label=self._section_label,
            records=self._tables.parse(section_fragment),
            metadata=build_section_metadata(
                parser=self.__class__.__name__,
                source="wikipedia",
            ),
        )


__all__ = ["ConstructorTablesSectionParser"]
