from typing import Any, TypedDict

from validation.records import RecordSchema
from validation.records import BaseDomainRecordValidator


class CircuitDetailsRecord(TypedDict):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]


CIRCUIT_DETAILS_SCHEMA = RecordSchema(
    required=("url", "infobox", "tables"),
    types={"url": str, "infobox": dict, "tables": list},
)


def validate_circuit_details_record(record: dict[str, Any]) -> list[str]:
    return BaseDomainRecordValidator.validate_schema(record, CIRCUIT_DETAILS_SCHEMA)
