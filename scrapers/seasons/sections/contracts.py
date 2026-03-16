from __future__ import annotations

from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult


class SeasonSectionParser(Protocol):
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult: ...
