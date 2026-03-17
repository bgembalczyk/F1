from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.interface import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.seasons.parsers.results import SeasonResultsParser


class SeasonResultsSectionParser:
    def __init__(self, parser: SeasonResultsParser) -> None:
        self._parser = parser

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = self._parser.parse(section_fragment)
        return SectionParseResult(
            section_id="Results",
            section_label="Results",
            records=records,
            metadata={"kind": "table"},
        )
