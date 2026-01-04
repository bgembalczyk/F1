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

    def to_dict(self) -> dict[str, Any]:
        return {
            "iso": self.iso,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "raw": self.raw,
        }
