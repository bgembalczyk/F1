from dataclasses import dataclass
from typing import Any

from models.wiki_url import WikiUrl


@dataclass(frozen=True)
class DriverRecordDTO:
    url: WikiUrl | str
    infobox: dict[str, Any]
    career_results: list[dict[str, Any]]
