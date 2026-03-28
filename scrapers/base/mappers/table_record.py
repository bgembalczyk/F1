from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Mapping


@dataclass(frozen=True)
class TableRecordInput:
    """Input contract for table row -> record mapper.

    Input: mapping-like row payload.
    Output: plain dict[str, Any].
    """

    payload: Mapping[str, Any]


@dataclass(frozen=True)
class LayoutTableRowsInput:
    """Input contract for layout table grouping mapper.

    Input: list of table rows with required `layout: str` field.
    Output: grouped list as {layout, lap_records} dictionaries.
    """

    rows: list[dict[str, Any]]


class TableRecordMapper:
    """Maps table rows to normalized dictionaries.

    Normalization rules:
    - row payload must be mapping,
    - key names are stringified and stripped,
    - nested mapping/list values are normalized recursively.
    """

    def map(self, payload: TableRecordInput | Mapping[str, Any]) -> dict[str, Any]:
        source = payload.payload if isinstance(payload, TableRecordInput) else payload
        if not isinstance(source, Mapping):
            msg = "Table mapper contract violation: payload must be mapping."
            raise TypeError(msg)
        return {
            str(key).strip(): self._normalize_value(value)
            for key, value in source.items()
        }

    def map_many(self, payloads: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [self.map(payload) for payload in payloads]

    def _normalize_value(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                str(k).strip(): self._normalize_value(v)
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [self._normalize_value(item) for item in value]
        return value


class LayoutTableRecordMapper:
    """Groups flat table rows into layout -> records structure.

    Normalization rules:
    - each row is first normalized with TableRecordMapper,
    - rows without non-empty layout string are ignored,
    - `layout` field is removed from grouped record entries.
    """

    def __init__(self, *, row_mapper: TableRecordMapper | None = None) -> None:
        self._row_mapper = row_mapper or TableRecordMapper()

    def map(self, payload: LayoutTableRowsInput | list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = payload.rows if isinstance(payload, LayoutTableRowsInput) else payload
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            normalized_row = self._row_mapper.map(row)
            layout_name = normalized_row.get("layout")
            if not isinstance(layout_name, str) or not layout_name.strip():
                continue
            row_export = {
                key: value
                for key, value in normalized_row.items()
                if key != "layout"
            }
            grouped.setdefault(layout_name.strip(), []).append(row_export)
        return [
            {"layout": name, "lap_records": records}
            for name, records in grouped.items()
        ]


__all__ = [
    "LayoutTableRecordMapper",
    "LayoutTableRowsInput",
    "TableRecordInput",
    "TableRecordMapper",
]
