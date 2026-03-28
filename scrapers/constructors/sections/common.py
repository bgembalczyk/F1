from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_metadata
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


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
            metadata=build_section_metadata(parser=self.__class__.__name__, source="wikipedia"),
        )
