from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.drivers.sections.common import BaseDriverResultsSectionParser
from scrapers.drivers.sections.common import DriverResultsSectionConfig
from scrapers.drivers.sections.constants import NON_CHAMPIONSHIP_SECTION

if TYPE_CHECKING:
    from scrapers.drivers.sections.results import DriverResultsSectionParser


class DriverNonChampionshipSectionParser(BaseDriverResultsSectionParser):
    def __init__(self, *, parser: DriverResultsSectionParser) -> None:
        super().__init__(
            parser=parser,
            section_id=NON_CHAMPIONSHIP_SECTION.section_id,
            section_label=NON_CHAMPIONSHIP_SECTION.section_label,
            header_aliases=NON_CHAMPIONSHIP_SECTION.header_aliases,
        )
