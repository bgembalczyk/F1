from typing import Any, TypedDict

from models.records.season import SEASON_SCHEMA
from models.records.season import SeasonRecord
from validation.records import NestedSchema
from validation.records import RecordSchema
from validation.records import RecordValidator


DRIVERS_CHAMPIONSHIPS_SCHEMA = RecordSchema(
    required=("count", "seasons"),
    types={"count": int, "seasons": list},
    nested={"seasons": NestedSchema(SEASON_SCHEMA, is_list=True)},
)


class DriversChampionshipsRecord(TypedDict):
    count: int
    seasons: list[SeasonRecord]


def validate_drivers_championships_record(record: dict[str, Any]) -> list[str]:
    return RecordValidator.validate_schema(record, DRIVERS_CHAMPIONSHIPS_SCHEMA)
