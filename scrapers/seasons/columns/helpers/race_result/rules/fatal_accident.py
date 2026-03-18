from typing import Any

from scrapers.seasons.columns.helpers.constants import FATAL_NOTES_START_YEAR
from scrapers.seasons.columns.helpers.race_result.helpers import append_note
from scrapers.seasons.columns.helpers.race_result.rules.context import ResultRuleContext


class FatalAccidentRule:
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        status, marks = self._status_and_marks(result, context)
        if status is None:
            return

        if self._is_before_race_fatality(status, marks):
            append_note(result, "fatal_accident_before_race")
            return
        if self._is_during_race_fatality(status, marks):
            append_note(result, "fatal_accident_during_race")

    @staticmethod
    def _status_and_marks(
        result: dict[str, Any],
        context: ResultRuleContext,
    ) -> tuple[str | None, list[str]]:
        marks = result.get("marks") or []
        position = result.get("position")
        if (
            context.season_year is None
            or context.season_year < FATAL_NOTES_START_YEAR
            or not isinstance(position, str)
        ):
            return None, marks
        return position.lower(), marks

    @staticmethod
    def _is_before_race_fatality(status: str, marks: list[str]) -> bool:
        return status == "dns" and "†" in marks

    @staticmethod
    def _is_during_race_fatality(status: str, marks: list[str]) -> bool:
        return status.startswith("ret") and ("†" in marks or "‡" in marks)
