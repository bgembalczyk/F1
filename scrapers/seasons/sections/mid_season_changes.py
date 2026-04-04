from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.serializer import build_section_parse_result

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.sections.interface import SectionParseResult


class SeasonMidSeasonChangesSectionParser:
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records = self._extract_list_items(section_fragment)
        if not records:
            records = [
                {"text": p.get_text(" ", strip=True)}
                for p in section_fragment.find_all("p")
                if p.get_text(" ", strip=True)
            ]
        return build_section_parse_result(
            section_id="mid-season_changes",
            section_label="Mid-season changes",
            records=records,
            parser=self.__class__.__name__,
            source="wikipedia",
            extras={"kind": "text"},
        )

    @staticmethod
    def _extract_list_items(section_fragment: BeautifulSoup) -> list[dict[str, str]]:
        records = [
            {"text": li.get_text(" ", strip=True)}
            for li in section_fragment.select("ul li")
            if li.get_text(" ", strip=True)
        ]
        if records:
            return records
        return [
            {"text": li.get_text(" ", strip=True)}
            for li in section_fragment.find_all("li")
            if li.get_text(" ", strip=True)
        ]
