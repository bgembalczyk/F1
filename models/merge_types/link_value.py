from __future__ import annotations

from dataclasses import dataclass

from models.merge_types.constants import RecordDict


@dataclass(frozen=True, slots=True)
class LinkValue:
    text: str
    url: str | None = None

    @classmethod
    def from_object(cls, value: object) -> LinkValue | None:
        if not isinstance(value, dict):
            return None
        record: RecordDict = value
        text = str(record.get("text") or "").strip()
        url = record.get("url")
        return cls(text=text, url=url if isinstance(url, str) and url else None)

    def to_dict(self) -> RecordDict:
        return {"text": self.text, "url": self.url}

    def dedupe_key(self) -> str | None:
        if self.url:
            return self.url
        if self.text:
            return self.text.casefold()
        return None
