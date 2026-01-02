from dataclasses import dataclass
from typing import Any
from typing import Mapping

from scrapers.base.helpers.value_objects.helpers import normalize_iso
from scrapers.base.helpers.value_objects.helpers import normalize_text


@dataclass(frozen=True)
class NormalizedDate:
    text: str | None = None
    iso: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", normalize_text(self.text))
        object.__setattr__(self, "iso", normalize_iso(self.iso))

    @classmethod
    def from_value(cls, value: Any):
        if value is None:
            return None
        if isinstance(value, NormalizedDate):
            return value
        if isinstance(value, Mapping):
            return cls(text=value.get("text"), iso=value.get("iso"))
        if isinstance(value, str):
            return cls(text=value, iso=None)
        return cls(text=str(value).strip(), iso=None)

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "iso": self.iso}
