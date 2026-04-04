from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from models.validation.utils import coerce_number
from models.validation.utils import is_valid_url
from models.value_objects.base import ValueObject

if TYPE_CHECKING:
    from collections.abc import Mapping


@dataclass
class SeasonRef(ValueObject):
    year: int
    url: str | None = None

    def __post_init__(self) -> None:
        self.year = coerce_number(self.year, int, "year")
        self.url = self.url or None
        if self.url:
            if not isinstance(self.url, str) or not is_valid_url(self.url):
                msg = "Pole seasons zawiera nieprawidłowy URL"
                raise ValueError(msg)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> SeasonRef | None:
        payload = data or {}
        year = payload.get("year")
        if year is None:
            return None
        return cls(year=year, url=payload.get("url"))

    def to_dict(self) -> dict[str, Any]:
        """Kontrakt eksportu sezonu używany przez rekordy i schematy walidacji."""
        result: dict[str, Any] = {"year": self.year}
        if self.url:
            result["url"] = self.url
        return result
