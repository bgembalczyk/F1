from typing import Any, TypedDict

from scrapers.base.validation import RecordValidator


class SeasonRecord(TypedDict):
    year: int
    url: str

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        errors.extend(RecordValidator.require_type(record, "year", int))
        errors.extend(RecordValidator.require_type(record, "url", str))
        return errors
