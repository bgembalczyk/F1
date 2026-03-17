from __future__ import annotations

from scrapers.base.sections.entry_factory import SectionEntrySpec
from scrapers.drivers.sections import DriverCareerSectionParser
from scrapers.drivers.sections import DriverNonChampionshipSectionParser
from scrapers.drivers.sections import DriverRacingRecordSectionParser
from scrapers.drivers.sections.results import DriverResultsSectionParser


def driver_section_specs(*, raw_parser: DriverResultsSectionParser) -> list[SectionEntrySpec]:
    return [
        SectionEntrySpec(
            section_id="Career_results",
            aliases=("Karting_record",),
            parser_factory=lambda: DriverCareerSectionParser(parser=raw_parser),
        ),
        SectionEntrySpec(
            section_id="Racing_record",
            aliases=("Motorsport_career_results",),
            parser_factory=lambda: DriverRacingRecordSectionParser(parser=raw_parser),
        ),
        SectionEntrySpec(
            section_id="Non-championship",
            aliases=("Non-championship_races",),
            parser_factory=lambda: DriverNonChampionshipSectionParser(parser=raw_parser),
        ),
    ]
