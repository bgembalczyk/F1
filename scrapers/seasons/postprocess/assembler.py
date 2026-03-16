from __future__ import annotations

from typing import Any


class SeasonRecordAssembler:
    def assemble(
        self,
        *,
        entries: list[dict[str, Any]],
        free_practice_drivers: list[dict[str, Any]],
        calendar: list[dict[str, Any]],
        cancelled_rounds: list[dict[str, Any]],
        testing_venues_and_dates: list[dict[str, Any]],
        results: list[dict[str, Any]],
        non_championship_races: list[dict[str, Any]],
        scoring_system: list[dict[str, Any]],
        drivers_standings: list[dict[str, Any]],
        constructors_standings: list[dict[str, Any]],
        jim_clark_trophy: list[dict[str, Any]],
        colin_chapman_trophy: list[dict[str, Any]],
        south_african_formula_one_championship: list[dict[str, Any]],
        british_formula_one_championship: list[dict[str, Any]],
        regulation_changes: list[dict[str, Any]],
        mid_season_changes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "entries": entries,
            "free_practice_drivers": free_practice_drivers,
            "calendar": calendar,
            "cancelled_rounds": cancelled_rounds,
            "testing_venues_and_dates": testing_venues_and_dates,
            "results": results,
            "non_championship_races": non_championship_races,
            "scoring_system": scoring_system,
            "drivers_standings": drivers_standings,
            "constructors_standings": constructors_standings,
            "jim_clark_trophy": jim_clark_trophy,
            "colin_chapman_trophy": colin_chapman_trophy,
            "south_african_formula_one_championship": south_african_formula_one_championship,
            "british_formula_one_championship": british_formula_one_championship,
            "regulation_changes": regulation_changes,
            "mid_season_changes": mid_season_changes,
        }
