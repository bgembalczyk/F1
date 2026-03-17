from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.interface import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class CircuitLayoutHistorySectionParser:
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        paragraphs = [
            p.get_text(" ", strip=True) for p in section_fragment.find_all("p")
        ]
        records = [{"text": text} for text in paragraphs if text]
        return SectionParseResult(
            section_id="layout_history",
            section_label="Layout history",
            records=records,
            metadata={"parser": self.__class__.__name__},
        )
