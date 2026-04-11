from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.parsers.seasons.results import SeasonResultsParser
from scrapers.parsers.roles import SectionParser
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonResultsSectionParser(SectionParser):
    def __init__(self, parser: SeasonResultsParser) -> None:
        self._parser = parser

    def parse(self, fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse(fragment)
        return build_section_parse_result(
            section_id="Results",
            section_label="Results",
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"kind": "table"},
        )


__all__ = ["SeasonResultsSectionParser"]
