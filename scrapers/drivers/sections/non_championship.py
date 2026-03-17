from __future__ import annotations

from scrapers.drivers.sections.common import BaseDriverResultsSectionParser
from scrapers.drivers.sections.common import DriverResultsSectionConfig
from scrapers.drivers.sections.results import DriverResultsSectionParser

NON_CHAMPIONSHIP_SECTION = DriverResultsSectionConfig(
    section_id="Non-championship",
    section_label="Non-championship",
    header_aliases=("Non-championship", "Non-championship races"),
)


class DriverNonChampionshipSectionParser(BaseDriverResultsSectionParser):
    def __init__(self, *, parser: DriverResultsSectionParser) -> None:
        super().__init__(
            parser=parser,
            section_id=NON_CHAMPIONSHIP_SECTION.section_id,
            section_label=NON_CHAMPIONSHIP_SECTION.section_label,
            header_aliases=NON_CHAMPIONSHIP_SECTION.header_aliases,
        )
