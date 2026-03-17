from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.drivers.sections.common import BaseDriverResultsSectionParser
from scrapers.drivers.sections.common import DriverResultsSectionConfig
from scrapers.drivers.sections.constants import CAREER_RESULTS_SECTION

if TYPE_CHECKING:
    from scrapers.drivers.sections.results import DriverResultsSectionParser


class DriverCareerSectionParser(BaseDriverResultsSectionParser):
    def __init__(self, *, parser: DriverResultsSectionParser) -> None:
        super().__init__(
            parser=parser,
            section_id=CAREER_RESULTS_SECTION.section_id,
            section_label=CAREER_RESULTS_SECTION.section_label,
            header_aliases=CAREER_RESULTS_SECTION.header_aliases,
        )
