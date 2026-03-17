from dataclasses import dataclass
from typing import Any
from typing import Protocol


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
    _CLASSIFIED_DNF_MARK = "†"
    _CLASSIFIED_DNF_NOTE = "classified_after_dnf_90_percent"
    _CLASSIFIED_DNF_START_YEAR = 1985
    _CLASSIFIED_DNF_BACKGROUNDS = {
        "Winner",
        "Second place",
        "Third place",
        "Other points position",
        "Other classified position",
    }

    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        marks = result.get("marks") or []
        position = result.get("position")
        if (
            context.season_year is not None
            and context.season_year >= self._CLASSIFIED_DNF_START_YEAR
            and self._CLASSIFIED_DNF_MARK in marks
            and context.background in self._CLASSIFIED_DNF_BACKGROUNDS
            and isinstance(position, int)
        ):
            append_note(result, self._CLASSIFIED_DNF_NOTE)


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
    _SHARED_DRIVE_NO_POINTS_START_YEAR = 1960
    _SHARED_DRIVE_NO_POINTS_END_YEAR = 1964
    _SHARED_DRIVE_POINTS_START_YEAR = 1950
    _SHARED_DRIVE_POINTS_END_YEAR = 1957

    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        marks = result.get("marks") or []
        if context.season_year is None or "†" not in marks:
            return

        if (
            self._SHARED_DRIVE_NO_POINTS_START_YEAR
            <= context.season_year
            <= self._SHARED_DRIVE_NO_POINTS_END_YEAR
        ):
            result["shared_drive"] = True
            result["points_eligible"] = False
            append_note(result, "shared_drive_no_points")
            return

        if (
            self._SHARED_DRIVE_POINTS_START_YEAR
            <= context.season_year
            <= self._SHARED_DRIVE_POINTS_END_YEAR
        ):
            result["shared_drive"] = True
            result["points_shared"] = True


class FatalAccidentRule:
    _FATAL_NOTES_START_YEAR = 1965

    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        marks = result.get("marks") or []
        position = result.get("position")
        if (
            context.season_year is None
            or context.season_year < self._FATAL_NOTES_START_YEAR
            or not isinstance(position, str)
        ):
            return

        status = position.lower()
        if status == "dns" and "†" in marks:
            append_note(result, "fatal_accident_before_race")
            return
        if status.startswith("ret") and ("†" in marks or "‡" in marks):
            append_note(result, "fatal_accident_during_race")


class F2EligibilityRule:
    _F2_INELIGIBLE_YEARS = {1957, 1958, 1966, 1967, 1969}

    def apply(self, result: dict[str, Any], context: ResultRuleContext) -> None:
        if context.season_year not in self._F2_INELIGIBLE_YEARS:
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
    _DOUBLE_POINTS_SEASON_YEAR = 2014

    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None:
        if (
            context.season_year == self._DOUBLE_POINTS_SEASON_YEAR
            and "Abu_Dhabi_Grand_Prix" in context.round_url
            and "‡" in context.marks
        ):
            return {"note": "double_points", "points_multiplier": 2.0}
        return None
