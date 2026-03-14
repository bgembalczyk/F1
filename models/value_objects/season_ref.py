from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from models.validation.utils import coerce_number
from models.validation.utils import is_valid_url
from models.value_objects.base import ValueObject


@dataclass
class SeasonRef(ValueObject):
    year: int
    url: str | None = None

    def __post_init__(self) -> None:
        self.year = coerce_number(self.year, int, "year")
        self.url = self.url or None
        if self.url:
            if not isinstance(self.url, str) or not is_valid_url(self.url):
                raise ValueError("Pole seasons zawiera nieprawidłowy URL")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "SeasonRef | None":
        payload = data or {}
        year = payload.get("year")
        if year is None:
            return None
        return cls(year=year, url=payload.get("url"))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"year": self.year}
        if self.url:
            result["url"] = self.url
        return result
