from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.drivers.sections.common import BaseDriverResultsSectionParser
from scrapers.drivers.sections.common import DriverResultsSectionConfig
from scrapers.drivers.sections.constants import RACING_RECORD_SECTION

if TYPE_CHECKING:
    from scrapers.drivers.sections.results import DriverResultsSectionParser


class DriverRacingRecordSectionParser(BaseDriverResultsSectionParser):
    def __init__(self, *, parser: DriverResultsSectionParser) -> None:
        super().__init__(
            parser=parser,
            section_id=RACING_RECORD_SECTION.section_id,
            section_label=RACING_RECORD_SECTION.section_label,
            header_aliases=RACING_RECORD_SECTION.header_aliases,
        )
