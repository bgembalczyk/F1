from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.drivers.sections.career import CAREER_RESULTS_SECTION
from scrapers.drivers.sections.common import BaseDriverResultsSectionParser
from scrapers.drivers.sections.common import DriverResultsSectionConfig
from scrapers.drivers.sections.constants import SECTION_CONFIGS
from scrapers.drivers.sections.results import DriverResultsSectionParser
from scrapers.wiki.parsers.section_profiles import profile_entry_aliases

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions


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
                    section_id=config.section_id,
                    aliases=profile_entry_aliases(
                        "drivers",
                        config.section_id,
                        *aliases,
                    ),
                    parser=BaseDriverResultsSectionParser.from_config(
                        parser=raw_parser,
                        config=config,
                    ),
                )
                for config, aliases in SECTION_CONFIGS
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
