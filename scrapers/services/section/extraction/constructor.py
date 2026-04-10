from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.adapters.section.constructors import constructor_section_entries
from scrapers.adapters.section.entry import SectionAdapterEntry
from scrapers.services.section.extraction.base import BaseSectionExtractionService


class ConstructorSectionExtractionService(BaseSectionExtractionService):
    domain = "constructors"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return constructor_section_entries()


__all__ = ["ConstructorSectionExtractionService"]
