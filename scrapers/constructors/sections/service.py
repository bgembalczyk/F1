from __future__ import annotations

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.base.sections.service import BaseSectionExtractionService
from scrapers.constructors.sections.adapter import constructor_section_entries


class ConstructorSectionExtractionService(BaseSectionExtractionService):
    domain = "constructors"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return constructor_section_entries()
