from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.contracts import SectionParserConfig
from scrapers.base.sections.contracts import SectionParserInput
from scrapers.base.sections.contracts import map_to_section_result
from scrapers.base.sections.interface import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.seasons.parsers.calendar import SeasonCalendarParser


class SeasonCalendarSectionParser:
    def __init__(self, parser: SeasonCalendarParser, season_year: int | None) -> None:
        self._parser = parser
        self._season_year = season_year

    def parse(
        self,
        section_fragment: BeautifulSoup | SectionParserInput,
    ) -> SectionParseResult:
        parser_input = (
            section_fragment
            if isinstance(section_fragment, SectionParserInput)
            else SectionParserInput(section_fragment=section_fragment)
        )
        records = self._parser.parse(
            parser_input.section_fragment,
            self._season_year,
        )
        return map_to_section_result(
            config=SectionParserConfig(
                section_id="Calendar",
                section_label="Calendar",
                parser_name=self.__class__.__name__,
                metadata_extras={"season_year": self._season_year, "kind": "table"},
            ),
            records=records,
        )
