from typing import Any, TypedDict

from validation.records import RecordValidator


class SeasonRecord(TypedDict):
    year: int
    url: str


def validate_season_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(RecordValidator.require_type(record, "year", int))
    errors.extend(RecordValidator.require_type(record, "url", str))
    return errors
