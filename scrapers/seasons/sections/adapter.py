from __future__ import annotations

from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.seasons.sections.calendar import SeasonCalendarSectionParser
from scrapers.seasons.sections.mid_season_changes import SeasonMidSeasonChangesSectionParser
from scrapers.seasons.sections.regulation_changes import SeasonRegulationChangesSectionParser
from scrapers.seasons.sections.results import SeasonResultsSectionParser
from scrapers.seasons.sections.standings import SeasonConstructorsStandingsSectionParser
from scrapers.seasons.sections.standings import SeasonDriversStandingsSectionParser


def season_section_entries(
    *,
    calendar_parser: SeasonCalendarSectionParser,
    results_parser: SeasonResultsSectionParser,
    drivers_standings_parser: SeasonDriversStandingsSectionParser,
    constructors_standings_parser: SeasonConstructorsStandingsSectionParser,
) -> list[SectionAdapterEntry]:
    return [
        SectionAdapterEntry(
            section_id="Calendar",
            aliases=("Grands_Prix",),
            parser=calendar_parser,
        ),
        SectionAdapterEntry(
            section_id="Results_and_standings",
            aliases=("Championship_standings",),
            parser=results_parser,
        ),
        SectionAdapterEntry(
            section_id="World_Drivers'_Championship_standings",
            aliases=("Drivers'_Championship",),
            parser=drivers_standings_parser,
        ),
        SectionAdapterEntry(
            section_id="World_Constructors'_Championship_standings",
            aliases=("Constructors'_Championship",),
            parser=constructors_standings_parser,
        ),
        SectionAdapterEntry(
            section_id="Regulation_changes",
            aliases=("Rule_changes",),
            parser=SeasonRegulationChangesSectionParser(),
        ),
        SectionAdapterEntry(
            section_id="Mid-season_changes",
            aliases=("Driver_changes",),
            parser=SeasonMidSeasonChangesSectionParser(),
        ),
    ]
