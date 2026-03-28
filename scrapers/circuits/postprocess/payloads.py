from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.base.payloads import InfoboxPayload
from scrapers.base.payloads import SectionsPayload
from scrapers.base.payloads import TablesPayload


@dataclass(frozen=True)
class CircuitTablePayload:
    layout: str
    lap_records: list[dict[str, Any]]

    def to_export(self) -> dict[str, Any]:
        return {
            "layout": self.layout,
            "lap_records": self.lap_records,
        }


@dataclass(frozen=True)
class CircuitTablesPayload(TablesPayload):
    tables: list[CircuitTablePayload]

    def __init__(self, tables: list[CircuitTablePayload]) -> None:
        super().__init__(data=[])
        object.__setattr__(self, "tables", tables)

    def to_export(self) -> list[dict[str, Any]]:
        return [table.to_export() for table in self.tables]


@dataclass(frozen=True)
class CircuitRecordPayload:
    infobox: InfoboxPayload
    tables: CircuitTablesPayload
    sections: SectionsPayload
