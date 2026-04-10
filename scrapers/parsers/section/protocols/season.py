from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

from scrapers.section.parse_results import SectionParseResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup



class SeasonSectionParser(Protocol):
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult: ...


__all__ = ["SeasonSectionParser"]
