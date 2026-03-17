from __future__ import annotations

from scrapers.drivers.sections.common import BaseDriverResultsSectionParser
from scrapers.drivers.sections.common import DriverResultsSectionConfig
from scrapers.drivers.sections.results import DriverResultsSectionParser

CAREER_RESULTS_SECTION = DriverResultsSectionConfig(
    section_id="Career_results",
    section_label="Career",
    header_aliases=("Career results", "Career"),
)


class DriverCareerSectionParser(BaseDriverResultsSectionParser):
    def __init__(self, *, parser: DriverResultsSectionParser) -> None:
        super().__init__(
            parser=parser,
            section_id=CAREER_RESULTS_SECTION.section_id,
            section_label=CAREER_RESULTS_SECTION.section_label,
            header_aliases=CAREER_RESULTS_SECTION.header_aliases,
        )
