from dataclasses import dataclass
from typing import Any
from typing import Mapping
from typing import Optional

from models.validation.utils import is_valid_url


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
    def from_dict(cls, data: Mapping[str, Any] | None):
        payload = data or {}
        return cls(text=payload.get("text") or "", url=payload.get("url"))

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "url": self.url}
