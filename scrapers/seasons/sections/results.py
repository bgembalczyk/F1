from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.contracts import SectionParserConfig
from scrapers.base.sections.contracts import SectionParserInput
from scrapers.base.sections.contracts import map_to_section_result
from scrapers.base.sections.interface import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.seasons.parsers.results import SeasonResultsParser


class SeasonResultsSectionParser:
    def __init__(self, parser: SeasonResultsParser) -> None:
        self._parser = parser

    def parse(
        self,
        section_fragment: BeautifulSoup | SectionParserInput,
    ) -> SectionParseResult:
        parser_input = (
            section_fragment
            if isinstance(section_fragment, SectionParserInput)
            else SectionParserInput(section_fragment=section_fragment)
        )
        records = self._parser.parse(parser_input.section_fragment)
        return map_to_section_result(
            config=SectionParserConfig(
                section_id="Results",
                section_label="Results",
                parser_name=self.__class__.__name__,
                metadata_extras={"kind": "table"},
            ),
            records=records,
        )
