from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.service import BaseSectionExtractionService
from scrapers.circuits.sections.adapter import circuit_section_entries

if TYPE_CHECKING:
    from scrapers.base.sections.adapter import SectionAdapterEntry


class CircuitSectionExtractionService(BaseSectionExtractionService):
    domain = "circuits"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return circuit_section_entries(
            options=self.require_options(),
            url=self.require_url(),
        )
