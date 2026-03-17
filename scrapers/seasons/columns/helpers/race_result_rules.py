from dataclasses import dataclass
from typing import Any
from typing import Protocol

from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_BACKGROUNDS
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_MARK
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_NOTE
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_START_YEAR
from scrapers.seasons.columns.helpers.constants import DOUBLE_POINTS_SEASON_YEAR
from scrapers.seasons.columns.helpers.constants import F2_INELIGIBLE_YEARS
from scrapers.seasons.columns.helpers.constants import FATAL_NOTES_START_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_NO_POINTS_END_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_NO_POINTS_START_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_POINTS_END_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_POINTS_START_YEAR


@dataclass(frozen=True)
class ResultRuleContext:
    season_year: int | None
    background: str | None
    footnotes: list[str]


class ResultRule(Protocol):
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None: ...


def append_note(result: dict[str, Any], note: str) -> None:
    notes = result.setdefault("notes", [])
    if note not in notes:
        notes.append(note)


class ClassifiedDnfRule:
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        if self._is_classified_dnf(result, context):
            append_note(result, CLASSIFIED_DNF_NOTE)

    @staticmethod
    def _is_classified_dnf(result: dict[str, Any], context: ResultRuleContext) -> bool:
        marks = result.get("marks") or []
        position = result.get("position")
        return (
            context.season_year is not None
            and context.season_year >= CLASSIFIED_DNF_START_YEAR
            and CLASSIFIED_DNF_MARK in marks
            and context.background in CLASSIFIED_DNF_BACKGROUNDS
            and isinstance(position, int)
        )


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
        return SHARED_DRIVE_NO_POINTS_START_YEAR <= season_year <= SHARED_DRIVE_NO_POINTS_END_YEAR

    @staticmethod
    def _is_shared_drive_with_points(season_year: int) -> bool:
        return SHARED_DRIVE_POINTS_START_YEAR <= season_year <= SHARED_DRIVE_POINTS_END_YEAR


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


class F2EligibilityRule:
    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        if context.season_year not in F2_INELIGIBLE_YEARS:
            return
        if "1" in context.footnotes:
            result["points_eligible"] = False
            append_note(result, "ineligible_f2")


class StarMarkNoteRule:
    def __init__(self, note: str) -> None:
        self._note = note

    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        marks = result.get("marks") or []
        if "*" in marks and context.background == "Other classified position":
            append_note(result, self._note)


@dataclass(frozen=True)
class RoundRuleContext:
    season_year: int | None
    marks: list[str]
    header_text: str
    round_url: str


class RoundRule(Protocol):
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None: ...


class HalfPointsRoundRule:
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None:
        if context.header_text == "500" or "Indianapolis_500" in context.round_url:
            return None
        if any(mark in {"*", "†", "‡"} for mark in context.marks):
            return {"note": "half_points", "points_multiplier": 0.5}
        return None


class DoublePointsRoundRule:
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None:
        if (
            context.season_year == DOUBLE_POINTS_SEASON_YEAR
            and "Abu_Dhabi_Grand_Prix" in context.round_url
            and "‡" in context.marks
        ):
            return {"note": "double_points", "points_multiplier": 2.0}
        return None
