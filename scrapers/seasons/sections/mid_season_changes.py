from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult


class SeasonMidSeasonChangesSectionParser:
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = [
            {"text": li.get_text(" ", strip=True)}
            for li in section_fragment.find_all("li")
            if li.get_text(" ", strip=True)
        ]
        return SectionParseResult(
            section_id="Mid-season_changes",
            section_label="Mid-season changes",
            records=records,
            metadata={"kind": "text"},
        )
