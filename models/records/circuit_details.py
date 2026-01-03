from typing import Any, TypedDict

from scrapers.base.validation import RecordValidator


class CircuitDetailsRecord(TypedDict):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]


def validate_circuit_details_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(RecordValidator.require_type(record, "url", str))
    errors.extend(RecordValidator.require_type(record, "infobox", dict))
    errors.extend(RecordValidator.require_type(record, "tables", list))
    return errors
