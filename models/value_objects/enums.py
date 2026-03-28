from __future__ import annotations

from enum import Enum


class ExportableEnum(str, Enum):
    @classmethod
    def from_raw(cls, value: str | "ExportableEnum") -> "ExportableEnum":
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError as exc:
            allowed = ", ".join(sorted(member.value for member in cls))
            msg = f"Unknown {cls.__name__}: {value!r}. Allowed values: {allowed}."
            raise ValueError(msg) from exc

    def to_export(self) -> str:
        return str(self.value)


class SectionIdEnum(ExportableEnum):
    DRIVER_RESULTS = "driver_results"
    CAREER_RESULTS = "Career_results"
    RACING_RECORD = "Racing_record"
    NON_CHAMPIONSHIP = "Non-championship"
    KARTING_RECORD = "Karting_record"
    MOTORSPORT_CAREER_RESULTS = "Motorsport_career_results"
    NON_CHAMPIONSHIP_RACES = "Non-championship_races"


class TableType(ExportableEnum):
    WIKI_TABLE = "wiki_table"
    STANDINGS = "standings"
    RACE_RESULTS = "race_results"
    LAP_RECORDS = "lap_records"
    CAREER_HIGHLIGHTS = "career_highlights"
    CAREER_SUMMARY = "career_summary"
    COMPLETE_RESULTS = "complete_results"


class MissingColumnsPolicy(ExportableEnum):
    SKIP = "skip"
    FAIL_IF_MISSING_SUBJECT_OR_POINTS = "fail_if_missing_subject_or_points"
    REQUIRE_ROUND_AND_WINNER = "require_round_and_winner"
    REQUIRE_TIME_AND_DRIVER = "require_time_and_driver"


class ExtraColumnsPolicy(ExportableEnum):
    IGNORE = "ignore"
    COLLECT_AS_ROUND_COLUMNS = "collect_as_round_columns"


class ValidationMode(ExportableEnum):
    SOFT = "soft"
    HARD = "hard"


class ConstructorStatus(ExportableEnum):
    ACTIVE = "active"
    FORMER = "former"
