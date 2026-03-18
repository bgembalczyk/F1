from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any
from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from models.records.record_definition import RecordDefinition
from models.records.record_definition import build_validator
from validation.domain_validator import BaseDomainRecordValidator
from validation.issue import ValidationIssue


EventFieldValue = str | LinkRecord | list[LinkRecord] | None


def validate_event_field(
    record: Mapping[str, Any],
) -> Sequence[ValidationIssue | str]:
    event = record.get("event")
    if isinstance(event, dict):
        return BaseDomainRecordValidator.prefix_errors(
            BaseDomainRecordValidator.validate_schema(event, LINK_SCHEMA),
            "event",
        )
    if isinstance(event, list):
        errors: list[ValidationIssue] = []
        for index, item in enumerate(event):
            if not isinstance(item, dict):
                errors.append(
                    ValidationIssue.custom(f"event[{index}] must be a mapping"),
                )
                continue
            errors.extend(
                BaseDomainRecordValidator.prefix_errors(
                    BaseDomainRecordValidator.validate_schema(item, LINK_SCHEMA),
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
    event: EventFieldValue
    championship: bool


EVENT_DEFINITION = RecordDefinition(
    name="event",
    types={"championship": bool},
    custom_validators=(validate_event_field,),
)

EVENT_SCHEMA = EVENT_DEFINITION.to_schema()
_EVENT_VALIDATOR = build_validator(EVENT_DEFINITION)


def validate_event_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return _EVENT_VALIDATOR(record)
