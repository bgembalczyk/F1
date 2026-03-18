from typing import Any
from typing import TypedDict

from validation.validator_base import RecordValidator
from validation.issue import ValidationIssue
from validation.schemas import RecordSchema


def validate_link_text(record: dict[str, Any]) -> list[ValidationIssue]:
    text = record.get("text")
    if isinstance(text, str) and not text.strip():
        return [ValidationIssue.custom("text must be a non-empty string")]
    return []


LINK_SCHEMA = RecordSchema(
    required=("text",),
    types={"text": str, "url": str},
    allow_none=("url",),
    custom_validators=(validate_link_text,),
)


class LinkRecord(TypedDict):
    text: str
    url: str | None


def validate_link_record(record: dict[str, Any]) -> list[ValidationIssue]:
    return RecordValidator.validate_schema(record, LINK_SCHEMA)
