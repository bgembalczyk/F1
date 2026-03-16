from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.sections.adapter import SectionAdapter
from scrapers.constructors.sections import constructor_section_entries


class ConstructorSectionExtractionService:
    def __init__(self, *, adapter: SectionAdapter) -> None:
        self._adapter = adapter

    def extract(self, soup: BeautifulSoup) -> list[dict[str, object]]:
        return self._adapter.parse_section_dicts(
            soup=soup,
            domain="constructors",
            entries=constructor_section_entries(),
        )
