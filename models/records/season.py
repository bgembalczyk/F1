from typing import Any
from typing import TypedDict

from validation.validator_base import RecordValidator
from validation.issue import ValidationIssue
from validation.schemas import RecordSchema

SEASON_SCHEMA = RecordSchema(
    required=("year", "url"),
    types={"year": int, "url": str},
)


class SeasonRecord(TypedDict):
    year: int
    url: str


def validate_season_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return RecordValidator.validate_schema(record, SEASON_SCHEMA)
