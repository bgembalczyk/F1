from typing import Any, Optional, TypedDict

from scrapers.base.validation import RecordValidator

from models.records.link import LinkRecord


class CarRecord(LinkRecord, total=False):
    formula_category: str

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        errors = RecordValidator.require_link_dict(record, "car")
        errors.extend(RecordValidator.require_type(record, "formula_category", str))
        return errors


class EventRecord(TypedDict, total=False):
    event: Optional[str | LinkRecord | list[LinkRecord]]
    championship: bool

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        event = record.get("event")
        if isinstance(event, dict):
            errors.extend(RecordValidator.require_link_dict(event, "event"))
        elif isinstance(event, list):
            errors.extend(RecordValidator.require_link_list(event, "event"))
        elif event is not None and not isinstance(event, str):
            errors.append("event must be a string, link, or list of links")
        errors.extend(RecordValidator.require_type(record, "championship", bool))
        return errors


class FatalityRecord(TypedDict, total=False):
    driver: LinkRecord
    date: Optional[str]
    age: Optional[int]
    event: Optional[EventRecord]
    circuit: Optional[LinkRecord]
    car: Optional[CarRecord]
    session: Optional[str]

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        driver = record.get("driver")
        if isinstance(driver, dict):
            errors.extend(RecordValidator.require_link_dict(driver, "driver"))
        elif driver is not None:
            errors.append("driver must be a link dict")

        event = record.get("event")
        if isinstance(event, dict):
            errors.extend(EventRecord.validate_record(event))
        elif event is not None:
            errors.append("event must be an event record")

        circuit = record.get("circuit")
        if isinstance(circuit, dict):
            errors.extend(RecordValidator.require_link_dict(circuit, "circuit"))
        elif circuit is not None:
            errors.append("circuit must be a link dict")

        car = record.get("car")
        if isinstance(car, dict):
            errors.extend(CarRecord.validate_record(car))
        elif car is not None:
            errors.append("car must be a car record")

        errors.extend(RecordValidator.require_type(record, "date", str, allow_none=True))
        errors.extend(RecordValidator.require_type(record, "age", int, allow_none=True))
        errors.extend(
            RecordValidator.require_type(record, "session", str, allow_none=True)
        )
        return errors
