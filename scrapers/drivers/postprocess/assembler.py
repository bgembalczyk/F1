from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models.value_objects import WikiUrl


@dataclass(frozen=True)
class DriverRecordDTO:
    url: WikiUrl | str
    infobox: dict[str, Any]
    career_results: list[dict[str, Any]]


class DriverRecordAssembler:
    def assemble(
        self,
        *,
        payload: DriverRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        return {
            "url": url.to_export(),
            "infobox": payload.infobox,
            "career_results": payload.career_results,
        }
