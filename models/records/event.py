from typing import Any
from typing import Optional
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from validation.records import RecordSchema
from validation.records import RecordValidator


def _validate_event_field(record: dict[str, Any]) -> list[str]:
    event = record.get("event")
    if isinstance(event, dict):
        return RecordValidator.validate_schema(event, LINK_SCHEMA)
    if isinstance(event, list):
        errors: list[str] = []
        for index, item in enumerate(event):
            if not isinstance(item, dict):
                errors.append(f"event[{index}] must be a mapping")
                continue
            errors.extend(
                RecordValidator._prefix_errors(
                    RecordValidator.validate_schema(item, LINK_SCHEMA),
                    f"event[{index}]",
                )
            )
        return errors
    if event is not None and not isinstance(event, str):
        return ["event must be a string, link, or list of links"]
    return []


class EventRecord(TypedDict, total=False):
    event: Optional[str | LinkRecord | list[LinkRecord]]
    championship: bool


EVENT_SCHEMA = RecordSchema(
    types={"championship": bool},
    custom_validators=(_validate_event_field,),
)


def validate_event_record(record: dict[str, Any]) -> list[str]:
    return RecordValidator.validate_schema(record, EVENT_SCHEMA)
