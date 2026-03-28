from typing import Any

from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_NO_POINTS_END_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_NO_POINTS_START_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_POINTS_END_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_POINTS_START_YEAR
from scrapers.seasons.columns.helpers.race_result.helpers import append_note
from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext


class SharedDriveRule:
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        marks = result.get("marks") or []
        if context.season_year is None or "†" not in marks:
            return

        if self._is_shared_drive_without_points(context.season_year):
            result["shared_drive"] = True
            result["points_eligible"] = False
            append_note(result, "shared_drive_no_points")
            return

        if self._is_shared_drive_with_points(context.season_year):
            result["shared_drive"] = True
            result["points_shared"] = True

    @staticmethod
    def _is_shared_drive_without_points(season_year: int) -> bool:
        return (
            SHARED_DRIVE_NO_POINTS_START_YEAR
            <= season_year
            <= SHARED_DRIVE_NO_POINTS_END_YEAR
        )

    @staticmethod
    def _is_shared_drive_with_points(season_year: int) -> bool:
        return (
            SHARED_DRIVE_POINTS_START_YEAR
            <= season_year
            <= SHARED_DRIVE_POINTS_END_YEAR
        )
