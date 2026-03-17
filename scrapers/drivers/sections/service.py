from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.sections.entry_factory import section_entries_from_specs
from scrapers.drivers.sections.results import DriverResultsSectionParser
from scrapers.drivers.sections.specs import driver_section_specs


class DriverSectionExtractionService:
    def __init__(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions,
        url: str,
    ) -> None:
        self._adapter = adapter
        self._options = options
        self._url = url

    def extract(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        raw_parser = DriverResultsSectionParser(options=self._options, url=self._url)
        sections = self._adapter.parse_sections(
            soup=soup,
            domain="drivers",
            entries=section_entries_from_specs(
                domain="drivers",
                specs=driver_section_specs(raw_parser=raw_parser),
            ),
        )

        records: list[dict[str, Any]] = []
        for section in sections:
            records.extend(
                {
                    **record,
                    "section": section.section_label,
                    "section_id": section.section_id,
                }
                for record in section.records
            )
        return records
