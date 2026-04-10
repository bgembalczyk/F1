from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.adapters.section.circuits import circuit_section_entries
from scrapers.adapters.section.entry import SectionAdapterEntry
from scrapers.services.section.extraction.base import BaseSectionExtractionService


class CircuitSectionExtractionService(BaseSectionExtractionService):
    domain = "circuits"

    def build_entries(self) -> list[SectionAdapterEntry]:
        return circuit_section_entries(
            options=self.require_options(),
            url=self.require_url(),
        )
