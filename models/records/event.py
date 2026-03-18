from typing import Any
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from validation.validator_base import RecordValidator
from validation.issue import ValidationIssue
from validation.schemas import RecordSchema


def validate_event_field(record: dict[str, Any]) -> list[ValidationIssue]:
    event = record.get("event")
    if isinstance(event, dict):
        return RecordValidator.validate_schema(event, LINK_SCHEMA)
    if isinstance(event, list):
        errors: list[ValidationIssue] = []
        for index, item in enumerate(event):
            if not isinstance(item, dict):
                errors.append(
                    ValidationIssue.custom(f"event[{index}] must be a mapping"),
                )
                continue
            errors.extend(
                RecordValidator.prefix_errors(
                    RecordValidator.validate_schema(item, LINK_SCHEMA),
                    f"event[{index}]",
                ),
            )
        return errors
    if event is not None and not isinstance(event, str):
        return [
            ValidationIssue.custom("event must be a string, link, or list of links"),
        ]
    return []


class EventRecord(TypedDict, total=False):
    event: str | LinkRecord | list[LinkRecord] | None
    championship: bool


EVENT_SCHEMA = RecordSchema(
    types={"championship": bool},
    custom_validators=(validate_event_field,),
)


def validate_event_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return RecordValidator.validate_schema(record, EVENT_SCHEMA)
