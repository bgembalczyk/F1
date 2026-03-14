from typing import Any
from typing import TypedDict

from models.records.car import CAR_SCHEMA
from models.records.car import CarRecord
from models.records.event import EVENT_SCHEMA
from models.records.event import EventRecord
from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from validation.records import BaseDomainRecordValidator
from validation.records import NestedSchema
from validation.records import RecordSchema
from validation.records import ValidationIssue


class FatalityRecord(TypedDict, total=False):
    driver: LinkRecord
    date: str | None
    age: int | None
    event: EventRecord | None
    circuit: LinkRecord | None
    car: CarRecord | None
    session: str | None


FATALITY_SCHEMA = RecordSchema(
    types={"date": str, "age": int, "session": str},
    allow_none=("date", "age", "session"),
    nested={
        "driver": NestedSchema(LINK_SCHEMA),
        "event": NestedSchema(EVENT_SCHEMA),
        "circuit": NestedSchema(LINK_SCHEMA),
        "car": NestedSchema(CAR_SCHEMA),
    },
)


def validate_fatality_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return BaseDomainRecordValidator.validate_schema(record, FATALITY_SCHEMA)
