from typing import Any, TypedDict

from scrapers.base.validation import RecordValidator


class LinkRecord(TypedDict):
    text: str
    url: str | None


def validate_link_record(record: dict[str, Any]) -> list[str]:
    return RecordValidator.require_link_dict(record, "link")
