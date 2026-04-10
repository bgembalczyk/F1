from dataclasses import dataclass
from typing import Any

from models.wiki_url import WikiUrl


@dataclass(frozen=True)
class ConstructorRecordDTO:
    url: WikiUrl | str
    infoboxes: list[dict[str, Any]]
    tables: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    metadata: dict[str, Any] | None = None
