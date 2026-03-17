from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SeasonRecordSections:
    entries: list[dict[str, Any]]
    free_practice_drivers: list[dict[str, Any]]
    calendar: list[dict[str, Any]]
    cancelled_rounds: list[dict[str, Any]]
    testing_venues_and_dates: list[dict[str, Any]]
    results: list[dict[str, Any]]
    non_championship_races: list[dict[str, Any]]
    scoring_system: list[dict[str, Any]]
    drivers_standings: list[dict[str, Any]]
    constructors_standings: list[dict[str, Any]]
    jim_clark_trophy: list[dict[str, Any]]
    colin_chapman_trophy: list[dict[str, Any]]
    south_african_formula_one_championship: list[dict[str, Any]]
    british_formula_one_championship: list[dict[str, Any]]
    regulation_changes: list[dict[str, Any]]
    mid_season_changes: list[dict[str, Any]]


class SeasonRecordAssembler:
    def assemble(self, sections: SeasonRecordSections) -> dict[str, Any]:
        return {
            "entries": sections.entries,
            "free_practice_drivers": sections.free_practice_drivers,
            "calendar": sections.calendar,
            "cancelled_rounds": sections.cancelled_rounds,
            "testing_venues_and_dates": sections.testing_venues_and_dates,
            "results": sections.results,
            "non_championship_races": sections.non_championship_races,
            "scoring_system": sections.scoring_system,
            "drivers_standings": sections.drivers_standings,
            "constructors_standings": sections.constructors_standings,
            "jim_clark_trophy": sections.jim_clark_trophy,
            "colin_chapman_trophy": sections.colin_chapman_trophy,
            "south_african_formula_one_championship": (
                sections.south_african_formula_one_championship
            ),
            "british_formula_one_championship": (
                sections.british_formula_one_championship
            ),
            "regulation_changes": sections.regulation_changes,
            "mid_season_changes": sections.mid_season_changes,
        }
