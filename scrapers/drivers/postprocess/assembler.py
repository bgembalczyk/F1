from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DriverRecordDTO:
    url: str
    infobox: dict[str, Any]
    career_results: list[dict[str, Any]]


class DriverRecordAssembler:
    def assemble(
        self,
        *,
        payload: DriverRecordDTO,
    ) -> dict[str, Any]:
        return {
            "url": payload.url,
            "infobox": payload.infobox,
            "career_results": payload.career_results,
        }
