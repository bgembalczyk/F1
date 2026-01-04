from typing import Any, TypedDict

from validation.records import RecordSchema
from validation.records import RecordValidator


SEASON_SCHEMA = RecordSchema(
    required=("year", "url"),
    types={"year": int, "url": str},
)


class SeasonRecord(TypedDict):
    year: int
    url: str


def validate_season_record(record: dict[str, Any]) -> list[str]:
    return RecordValidator.validate_schema(record, SEASON_SCHEMA)
