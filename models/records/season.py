from typing import Any
from typing import TypedDict

from validation.records import BaseDomainRecordValidator
from validation.records import RecordSchema
from validation.records import ValidationIssue

SEASON_SCHEMA = RecordSchema(
    required=("year", "url"),
    types={"year": int, "url": str},
)


class SeasonRecord(TypedDict):
    year: int
    url: str


def validate_season_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return BaseDomainRecordValidator.validate_schema(record, SEASON_SCHEMA)
