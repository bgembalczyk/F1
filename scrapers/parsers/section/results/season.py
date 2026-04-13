from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.parsers.section.base import SectionParserBase
from scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.results import (
    SeasonResultsParser,
)
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonResultsSectionParser(SectionParserBase):
    def __init__(self, parser: SeasonResultsParser) -> None:
        self._parser = parser

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse(section_fragment)
        return build_section_parse_result(
            section_id="Results",
            section_label="Results",
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"kind": "table"},
        )


__all__ = ["SeasonResultsSectionParser"]
