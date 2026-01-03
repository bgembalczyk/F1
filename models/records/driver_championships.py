from typing import Any, TypedDict

from models.records.season import SeasonRecord
from validation.records import RecordValidator


class DriversChampionshipsRecord(TypedDict):
    count: int
    seasons: list[SeasonRecord]


def validate_drivers_championships_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(RecordValidator.require_type(record, "count", int))
    errors.extend(RecordValidator.require_type(record, "seasons", list))
    return errors
