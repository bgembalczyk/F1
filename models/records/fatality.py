from typing import Any, Optional, TypedDict

from models.records.car import CarRecord
from models.records.car import validate_car_record
from models.records.event import EventRecord
from models.records.event import validate_event_record
from models.records.link import LinkRecord
from validation.records import RecordValidator


class FatalityRecord(TypedDict, total=False):
    driver: LinkRecord
    date: Optional[str]
    age: Optional[int]
    event: Optional[EventRecord]
    circuit: Optional[LinkRecord]
    car: Optional[CarRecord]
    session: Optional[str]


def validate_fatality_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    driver = record.get("driver")
    if isinstance(driver, dict):
        errors.extend(RecordValidator.require_link_dict(driver, "driver"))
    elif driver is not None:
        errors.append("driver must be a link dict")

    event = record.get("event")
    if isinstance(event, dict):
        errors.extend(validate_event_record(event))
    elif event is not None:
        errors.append("event must be an event record")

    circuit = record.get("circuit")
    if isinstance(circuit, dict):
        errors.extend(RecordValidator.require_link_dict(circuit, "circuit"))
    elif circuit is not None:
        errors.append("circuit must be a link dict")

    car = record.get("car")
    if isinstance(car, dict):
        errors.extend(validate_car_record(car))
    elif car is not None:
        errors.append("car must be a car record")

    errors.extend(RecordValidator.require_type(record, "date", str, allow_none=True))
    errors.extend(RecordValidator.require_type(record, "age", int, allow_none=True))
    errors.extend(RecordValidator.require_type(record, "session", str, allow_none=True))
    return errors
