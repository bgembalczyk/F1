from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.contracts import SectionParserConfig
from scrapers.base.sections.contracts import SectionParserInput
from scrapers.base.sections.contracts import map_to_section_result
from scrapers.base.sections.interface import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonMidSeasonChangesSectionParser:
    def parse(
        self,
        section_fragment: BeautifulSoup | SectionParserInput,
    ) -> SectionParseResult:
        parser_input = (
            section_fragment
            if isinstance(section_fragment, SectionParserInput)
            else SectionParserInput(section_fragment=section_fragment)
        )
        records = [
            {"text": li.get_text(" ", strip=True)}
            for li in parser_input.section_fragment.find_all("li")
            if li.get_text(" ", strip=True)
        ]
        return map_to_section_result(
            config=SectionParserConfig(
                section_id="Mid-season_changes",
                section_label="Mid-season changes",
                parser_name=self.__class__.__name__,
                metadata_extras={"kind": "text"},
            ),
            records=records,
        )
