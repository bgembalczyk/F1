from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from models.value_objects.base import ValueObject


@dataclass(frozen=True)
class DateValue(ValueObject):
    iso: str | list[str] | None = None
    year: int | None = None
    month: int | None = None
    day: int | None = None
    raw: str | None = None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "DateValue":
        return cls(**dict(data))

    def to_dict(self) -> dict[str, Any]:
        """Kontrakt eksportu pełnej reprezentacji daty dla warstw I/O."""
        return {
            "iso": self.iso,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "raw": self.raw,
        }
