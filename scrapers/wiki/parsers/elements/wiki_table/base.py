from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class WikiTableBaseParser(ABC):
    table_type: str = "wiki_table"
    missing_columns_policy: str = "skip"
    extra_columns_policy: str = "ignore"

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
