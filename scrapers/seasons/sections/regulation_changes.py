from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_metadata

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SeasonRegulationChangesSectionParser:
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = [
            {"text": li.get_text(" ", strip=True)}
            for li in section_fragment.find_all("li")
            if li.get_text(" ", strip=True)
        ]
        if not records:
            records = [
                {"text": p.get_text(" ", strip=True)}
                for p in section_fragment.find_all("p")
                if p.get_text(" ", strip=True)
            ]
        return SectionParseResult(
            section_id="Regulation_changes",
            section_label="Regulation changes",
            records=records,
            metadata=build_section_metadata(parser=self.__class__.__name__, source="wikipedia", extras={"kind": "text"}),
        )
