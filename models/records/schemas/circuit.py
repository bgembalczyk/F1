from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import ClassVar

from models.records.schemas.base import ExportSchemaModel


@dataclass(frozen=True)
class CircuitExportRecord(ExportSchemaModel):
    url: str
    infobox: dict[str, Any]
    tables: list[dict[str, Any]]
    sections: list[dict[str, Any]]

    contract_fields: ClassVar[tuple[str, ...]] = (
        "url",
        "infobox",
        "tables",
        "sections",
    )
