from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_parse_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class CircuitLayoutHistorySectionParser:
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        paragraphs = [
            p.get_text(" ", strip=True) for p in section_fragment.find_all("p")
        ]
        records = [{"text": text} for text in paragraphs if text]
        return build_section_parse_result(
            section_id="layout_history",
            section_label="Layout history",
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
        )
