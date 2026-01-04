from typing import Any, Optional, TypedDict

from models.records.car import CAR_SCHEMA
from models.records.car import CarRecord
from models.records.event import EVENT_SCHEMA
from models.records.event import EventRecord
from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from validation.records import NestedSchema
from validation.records import RecordSchema
from validation.records import BaseDomainRecordValidator


class FatalityRecord(TypedDict, total=False):
    driver: LinkRecord
    date: Optional[str]
    age: Optional[int]
    event: Optional[EventRecord]
    circuit: Optional[LinkRecord]
    car: Optional[CarRecord]
    session: Optional[str]


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


def validate_fatality_record(record: dict[str, Any]) -> list[str]:
    return BaseDomainRecordValidator.validate_schema(record, FATALITY_SCHEMA)
