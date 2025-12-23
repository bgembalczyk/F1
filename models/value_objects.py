from dataclasses import dataclass
from typing import Any, Mapping, Optional

from models.validation.utils import coerce_number, is_valid_url


@dataclass
class Link:
    text: str = ""
    url: Optional[str] = None

    def __post_init__(self) -> None:
        self.text = str(self.text or "").strip()
        self.url = self.url or None
        if self.url:
            if not isinstance(self.url, str) or not is_valid_url(self.url):
                raise ValueError("Pole link zawiera nieprawidłowy URL")

    def is_empty(self) -> bool:
        return not self.text and self.url is None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> Link:
        payload = data or {}
        return cls(text=payload.get("text") or "", url=payload.get("url"))

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "url": self.url}


@dataclass
class SeasonRef:
    year: int
    url: Optional[str] = None

    def __post_init__(self) -> None:
        self.year = coerce_number(self.year, int, "year")
        self.url = self.url or None
        if self.url:
            if not isinstance(self.url, str) or not is_valid_url(self.url):
                raise ValueError("Pole seasons zawiera nieprawidłowy URL")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> SeasonRef | None:
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
