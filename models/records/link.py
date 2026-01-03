from typing import Any, TypedDict

from scrapers.base.validation import RecordValidator


class LinkRecord(TypedDict):
    text: str
    url: str | None

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        return RecordValidator.require_link_dict(record, "link")
