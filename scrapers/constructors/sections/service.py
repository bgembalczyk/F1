from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.constructors.sections import constructor_section_entries

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.sections.adapter import SectionAdapter


class ConstructorSectionExtractionService:
    def __init__(self, *, adapter: SectionAdapter) -> None:
        self._adapter = adapter

    def extract(self, soup: BeautifulSoup) -> list[dict[str, object]]:
        return self._adapter.parse_section_dicts(
            soup=soup,
            domain="constructors",
            entries=constructor_section_entries(),
        )
