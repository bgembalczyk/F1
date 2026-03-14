from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from models.value_objects.base import ValueObject
from models.value_objects.link_utils import validate_link


@dataclass
class Link(ValueObject):
    text: str = ""
    url: str | None = None

    def __post_init__(self) -> None:
        normalized = validate_link(
            {"text": self.text, "url": self.url},
            field_name="link",
        )
        self.text = normalized["text"]
        self.url = normalized["url"]

    def is_empty(self) -> bool:
        return not self.text and self.url is None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "Link":
        payload = data or {}
        return cls(text=payload.get("text") or "", url=payload.get("url"))

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "url": self.url}
