from typing import Any

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from validation.records import RecordSchema
from validation.records import BaseDomainRecordValidator


class CarRecord(LinkRecord, total=False):
    formula_category: str


CAR_SCHEMA = RecordSchema(
    required=(*LINK_SCHEMA.required, "formula_category"),
    types={**LINK_SCHEMA.types, "formula_category": str},
    allow_none=LINK_SCHEMA.allow_none,
    custom_validators=LINK_SCHEMA.custom_validators,
)


def validate_car_record(record: dict[str, Any]) -> list[str]:
    return BaseDomainRecordValidator.validate_schema(record, CAR_SCHEMA)
