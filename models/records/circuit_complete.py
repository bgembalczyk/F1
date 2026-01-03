from typing import Any, TypedDict

from scrapers.base.validation import RecordValidator

from models.records.link import LinkRecord
from models.records.season import SeasonRecord


class CircuitCompleteRecord(TypedDict, total=False):
    name: dict[str, Any]
    url: str | None
    circuit_status: str
    type: str | None
    direction: str | None
    grands_prix: list[LinkRecord]
    seasons: list[SeasonRecord]
    grands_prix_held: int | None
    location: dict[str, Any]
    fia_grade: str
    history: list[Any]
    layouts: list[dict[str, Any]]

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        errors.extend(RecordValidator.require_type(record, "name", dict, allow_none=True))
        errors.extend(RecordValidator.require_type(record, "url", str, allow_none=True))
        errors.extend(
            RecordValidator.require_type(record, "circuit_status", str, allow_none=True)
        )
        errors.extend(RecordValidator.require_type(record, "type", str, allow_none=True))
        errors.extend(
            RecordValidator.require_type(record, "direction", str, allow_none=True)
        )
        errors.extend(
            RecordValidator.require_type(record, "grands_prix", list, allow_none=True)
        )
        errors.extend(
            RecordValidator.require_type(record, "seasons", list, allow_none=True)
        )
        errors.extend(
            RecordValidator.require_type(record, "grands_prix_held", int, allow_none=True)
        )
        errors.extend(
            RecordValidator.require_type(record, "location", dict, allow_none=True)
        )
        errors.extend(
            RecordValidator.require_type(record, "fia_grade", str, allow_none=True)
        )
        errors.extend(
            RecordValidator.require_type(record, "history", list, allow_none=True)
        )
        errors.extend(
            RecordValidator.require_type(record, "layouts", list, allow_none=True)
        )
        return errors
