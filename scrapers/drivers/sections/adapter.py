from __future__ import annotations

from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.drivers.sections.career import DriverCareerSectionParser
from scrapers.drivers.sections.non_championship import DriverNonChampionshipSectionParser
from scrapers.drivers.sections.racing_record import DriverRacingRecordSectionParser
from scrapers.drivers.sections.results import DriverResultsSectionParser


def driver_section_entries(*, options: ScraperOptions, url: str) -> list[SectionAdapterEntry]:
    raw_parser = DriverResultsSectionParser(options=options, url=url)
    return [
        SectionAdapterEntry(
            section_id="Career_results",
            aliases=("Karting_record",),
            parser=DriverCareerSectionParser(parser=raw_parser),
        ),
        SectionAdapterEntry(
            section_id="Racing_record",
            aliases=("Motorsport_career_results",),
            parser=DriverRacingRecordSectionParser(parser=raw_parser),
        ),
        SectionAdapterEntry(
            section_id="Non-championship",
            aliases=("Non-championship_races",),
            parser=DriverNonChampionshipSectionParser(parser=raw_parser),
        ),
    ]
