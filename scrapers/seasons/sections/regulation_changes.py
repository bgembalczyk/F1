from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult


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
            metadata={"kind": "text"},
        )
