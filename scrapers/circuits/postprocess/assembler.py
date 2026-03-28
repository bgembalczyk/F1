from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models.value_objects import WikiUrl


@dataclass(frozen=True)
class CircuitLapRecordLayoutDTO:
    layout: str
    lap_records: list[dict[str, Any]]


@dataclass(frozen=True)
class CircuitRecordDTO:
    url: WikiUrl | str
    infobox: dict[str, Any]
    lap_record_rows: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class CircuitRecordAssembler:
    def assemble_tables(
        self,
        *,
        lap_record_rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in lap_record_rows:
            layout_name = row.get("layout")
            if not isinstance(layout_name, str) or not layout_name:
                continue
            row_export = {k: v for k, v in row.items() if k != "layout"}
            grouped.setdefault(layout_name, []).append(row_export)
        return [
            CircuitLapRecordLayoutDTO(layout=name, lap_records=records).__dict__
            for name, records in grouped.items()
        ]

    def assemble(
        self,
        *,
        payload: CircuitRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        return {
            "url": url.to_export(),
            "infobox": payload.infobox,
            "tables": self.assemble_tables(lap_record_rows=payload.lap_record_rows),
            "sections": payload.sections,
        }
