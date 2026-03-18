from typing import Any

from scrapers.seasons.columns.helpers.race_result.helpers import append_note
from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext


class MarkBasedEligibilityRule:
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        marks = result.get("marks") or []
        position = result.get("position")
        if "*" in marks and context.background == "Other classified position":
            result["points_eligible"] = False
        if "~" in marks:
            result["points_eligible"] = False
            append_note(result, "shared_drive_no_points")
        if "‡" in marks and isinstance(position, int):
            result["points_eligible"] = False
            append_note(result, "no_points_awarded")
