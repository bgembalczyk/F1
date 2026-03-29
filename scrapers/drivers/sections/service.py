from __future__ import annotations

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.base.sections.service import BaseSectionExtractionService
from scrapers.drivers.sections.common import BaseDriverResultsSectionParser
from scrapers.drivers.sections.constants import SECTION_CONFIGS
from scrapers.drivers.sections.results import DriverResultsSectionParser
from scrapers.wiki.parsers.sections.helpers import profile_entry_aliases


class DriverSectionExtractionService(BaseSectionExtractionService):
    domain = "drivers"
    flatten_records = True

    def build_entries(self) -> list[SectionAdapterEntry]:
        raw_parser = DriverResultsSectionParser(
            options=self.require_options(),
            url=self.require_url(),
        )
        return [
            SectionAdapterEntry(
                section_id=config.section_id,
                aliases=profile_entry_aliases(
                    self.domain,
                    config.section_id,
                    *aliases,
                ),
                parser=BaseDriverResultsSectionParser.from_config(
                    parser=raw_parser,
                    config=config,
                ),
            )
            for config, aliases in SECTION_CONFIGS
        ]
