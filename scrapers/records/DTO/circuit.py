from dataclasses import dataclass
from typing import Any

from models.wiki_url import WikiUrl


@dataclass(frozen=True)
class CircuitRecordDTO:
    url: WikiUrl | str
    infobox: dict[str, Any]
    lap_record_rows: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    metadata: dict[str, Any] | None = None
