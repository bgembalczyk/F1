from typing import Any

from models.records.circuit_base import CIRCUIT_BASE_SCHEMA
from models.records.circuit_base import CircuitBaseRecord
from validation.domain_validator import BaseDomainRecordValidator
from validation.issue import ValidationIssue
from validation.schemas import RecordSchema


class CircuitDetailsRecord(CircuitBaseRecord):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]


CIRCUIT_DETAILS_SCHEMA = RecordSchema(
    required=("url", "infobox", "tables"),
    types={**CIRCUIT_BASE_SCHEMA.types, "infobox": dict, "tables": list},
)


def validate_circuit_details_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return BaseDomainRecordValidator.validate_schema(record, CIRCUIT_DETAILS_SCHEMA)
