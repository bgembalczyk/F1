from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class WikiTableBaseParser(ABC):
    table_type: str = "wiki_table"
    missing_columns_policy: str = "skip"
    extra_columns_policy: str = "ignore"

    def collect_rows(self, payload: Any) -> list[dict[str, Any]]:
        """Traverse parsed payload and collect all domain rows matching this table type.

        The payload may be a nested dict/list structure produced by section parsers.
        Every node whose ``table_type`` equals ``self.table_type`` contributes its
        ``domain_rows`` list to the result.
        """
        rows: list[dict[str, Any]] = []
        self._collect_from_node(payload, rows)
        return rows

    def _collect_from_node(self, node: Any, rows: list[dict[str, Any]]) -> None:
        if isinstance(node, dict):
            if node.get("table_type") == self.table_type:
                table_rows = node.get("domain_rows", [])
                if isinstance(table_rows, list):
                    rows.extend(row for row in table_rows if isinstance(row, dict))
            for value in node.values():
                self._collect_from_node(value, rows)
        elif isinstance(node, list):
            for item in node:
                self._collect_from_node(item, rows)

    def parse(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        headers = table_data.get("headers", [])
        if not isinstance(headers, list) or not self.matches(headers, table_data):
            return None

        column_map = self.map_columns(headers)
        normalized_rows = self._normalized_rows(table_data)
        mapped_rows = [self._map_row(row, column_map) for row in normalized_rows]

        return {
            "table_type": self.table_type,
            "domain_column_map": column_map,
            "missing_columns_policy": self.missing_columns_policy,
            "extra_columns_policy": self.extra_columns_policy,
            "domain_rows": mapped_rows,
        }

    @staticmethod
    def _normalized_rows(table_data: dict[str, Any]) -> list[dict[str, Any]]:
        rows = table_data.get("rows", [])
        if isinstance(rows, list):
            dict_rows = [row for row in rows if isinstance(row, dict)]
            if dict_rows:
                return dict_rows

        raw_rows = table_data.get("raw_rows", [])
        if isinstance(raw_rows, list):
            return [row for row in raw_rows if isinstance(row, dict)]

        return []

    @abstractmethod
    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        """Czy parser pasuje do konkretnej tabeli."""

    @abstractmethod
    def map_columns(self, headers: list[str]) -> dict[str, str]:
        """Mapuje nagłówki tabeli na pola domenowe."""

    @staticmethod
    def _map_row(row: dict[str, Any], column_map: dict[str, str]) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for header, value in row.items():
            key = column_map.get(header)
            if key:
                mapped[key] = value
        return mapped
