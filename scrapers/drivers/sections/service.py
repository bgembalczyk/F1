from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.drivers.sections import DriverCareerSectionParser
from scrapers.drivers.sections import DriverNonChampionshipSectionParser
from scrapers.drivers.sections import DriverRacingRecordSectionParser
from scrapers.drivers.sections.results import DriverResultsSectionParser
from scrapers.wiki.parsers.section_profiles import profile_entry_aliases


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
            entries=[
                SectionAdapterEntry(
                    section_id="Career_results",
                    aliases=profile_entry_aliases(
                        "drivers",
                        "Career_results",
                        "Karting_record",
                    ),
                    parser=DriverCareerSectionParser(parser=raw_parser),
                ),
                SectionAdapterEntry(
                    section_id="Racing_record",
                    aliases=profile_entry_aliases(
                        "drivers",
                        "Racing_record",
                        "Motorsport_career_results",
                    ),
                    parser=DriverRacingRecordSectionParser(parser=raw_parser),
                ),
                SectionAdapterEntry(
                    section_id="Non-championship",
                    aliases=profile_entry_aliases(
                        "drivers",
                        "Non-championship",
                        "Non-championship_races",
                    ),
                    parser=DriverNonChampionshipSectionParser(parser=raw_parser),
                ),
            ],
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
