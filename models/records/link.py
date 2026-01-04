from typing import Any, TypedDict

from validation.records import RecordSchema
from validation.records import RecordValidator


def _validate_link_text(record: dict[str, Any]) -> list[str]:
    text = record.get("text")
    if isinstance(text, str) and not text.strip():
        return ["text must be a non-empty string"]
    return []


LINK_SCHEMA = RecordSchema(
    required=("text",),
    types={"text": str, "url": str},
    allow_none=("url",),
    custom_validators=(_validate_link_text,),
)


class LinkRecord(TypedDict):
    text: str
    url: str | None


def validate_link_record(record: dict[str, Any]) -> list[str]:
    return RecordValidator.validate_schema(record, LINK_SCHEMA)
