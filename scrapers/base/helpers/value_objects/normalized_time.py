from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from models.value_objects.helpers import normalize_text
from scrapers.base.helpers.value_objects.helpers import normalize_seconds


@dataclass(frozen=True)
class NormalizedTime:
    text: str | None = None
    seconds: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", normalize_text(self.text))
        object.__setattr__(self, "seconds", normalize_seconds(self.seconds))

    @classmethod
    def from_value(cls, value: Any):
        if value is None:
            return None
        if isinstance(value, NormalizedTime):
            return value
        if isinstance(value, Mapping):
            return cls(text=value.get("text"), seconds=value.get("seconds"))
        if isinstance(value, (int, float)):
            return cls(text=None, seconds=float(value))
        return cls(text=str(value).strip(), seconds=None)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "seconds": self.seconds}
