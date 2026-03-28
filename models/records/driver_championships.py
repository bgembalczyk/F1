from typing import Any
from typing import TypedDict

from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.issue import ValidationIssue
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema
from validation.validator_base import RecordValidator

DRIVERS_CHAMPIONSHIPS_SCHEMA = RecordSchema(
    required=("count", "seasons"),
    types={"count": int, "seasons": list},
    nested={"seasons": NestedSchema(SEASON_SCHEMA, is_list=True)},
)


class DriversChampionshipsRecord(TypedDict):
    count: int
    seasons: list[SeasonRecord]


def validate_drivers_championships_record(
    record: dict[str, Any],
) -> list[ValidationIssue]:
    return RecordValidator.validate_schema(
        record,
        DRIVERS_CHAMPIONSHIPS_SCHEMA,
    )
