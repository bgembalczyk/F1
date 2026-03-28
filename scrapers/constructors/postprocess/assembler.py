from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConstructorRecordDTO:
    url: str
    infoboxes: list[dict[str, Any]]
    tables: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class ConstructorRecordAssembler:
    def assemble(
        self,
        *,
        payload: ConstructorRecordDTO,
    ) -> dict[str, Any]:
        return {
            "url": payload.url,
            "infoboxes": payload.infoboxes,
            "tables": payload.tables,
            "sections": payload.sections,
        }
