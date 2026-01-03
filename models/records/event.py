from typing import Any
from typing import Optional
from typing import TypedDict

from models.records.link import LinkRecord
from validation.records import RecordValidator


class EventRecord(TypedDict, total=False):
    event: Optional[str | LinkRecord | list[LinkRecord]]
    championship: bool


def validate_event_record(record: dict[str, Any]) -> list[str]:
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
