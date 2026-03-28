from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.service import BaseSectionExtractionService
from scrapers.constructors.sections.adapter import constructor_section_entries

if TYPE_CHECKING:
    from scrapers.base.sections.adapter import SectionAdapterEntry


class ConstructorSectionExtractionService(BaseSectionExtractionService):
    domain = "constructors"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return constructor_section_entries()
