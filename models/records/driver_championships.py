from typing import Any, TypedDict

from scrapers.base.validation import RecordValidator

from models.records.season import SeasonRecord


class DriversChampionshipsRecord(TypedDict):
    count: int
    seasons: list[SeasonRecord]

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        errors.extend(RecordValidator.require_type(record, "count", int))
        errors.extend(RecordValidator.require_type(record, "seasons", list))
        return errors
