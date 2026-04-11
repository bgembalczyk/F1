from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Protocol


class TableFragmentParserProtocol(Protocol):
    """Typing-only kontrakt parsera fragmentu tabeli."""

    def parse(self, raw_html_fragment: dict[str, Any]) -> dict[str, Any] | None: ...


class AbstractTableFragmentParser(ABC):
    """Bazowa klasa runtime dla parserów fragmentów tabel Wikipedii."""

    @abstractmethod
    def parse(self, fragment: dict[str, Any]) -> dict[str, Any] | None:
        """Parsuje fragment tabeli do reprezentacji domenowej."""


class WikiTablePayloadTransformer:
    """Transforms parsed section payloads by mapping table elements to domain tables."""

    def __init__(self, parser: TableFragmentParserProtocol) -> None:
        self._parser = parser

    def transform(self, parsed_fragment: dict[str, Any]) -> dict[str, Any]:
        self._apply_to_elements(parsed_fragment.get("elements", []))
        for value in parsed_fragment.values():
            if isinstance(value, dict):
                self.transform(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.transform(item)
        return parsed_fragment

    def _apply_to_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._parser.parse(data)
            if parsed is not None:
                element["data"] = parsed


class WikiTablePayloadCollector:
    """Collect domain rows from nested payload trees for a concrete table type."""

    def __init__(self, table_type: str) -> None:
        self._table_type = table_type

    def collect(self, payload_tree: Any) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        self._collect_from_node(payload_tree, rows)
        return rows

    def _collect_from_node(self, node: Any, rows: list[dict[str, Any]]) -> None:
        if isinstance(node, dict):
            if node.get("table_type") == self._table_type:
                table_rows = node.get("domain_rows", [])
                if isinstance(table_rows, list):
                    rows.extend(row for row in table_rows if isinstance(row, dict))
            for value in node.values():
                self._collect_from_node(value, rows)
        elif isinstance(node, list):
            for item in node:
                self._collect_from_node(item, rows)


class WikiTableBaseParser(AbstractTableFragmentParser):
    table_type: str = "wiki_table"
    missing_columns_policy: str = "skip"
    extra_columns_policy: str = "ignore"
    required_header_groups: tuple[frozenset[str], ...] = ()
    column_mapping: dict[str, str] = {}

    def parse(self, fragment: dict[str, Any]) -> dict[str, Any] | None:
        return self.parse_fragment(fragment)

    def parse_fragment(self, fragment: dict[str, Any]) -> dict[str, Any] | None:
        headers = fragment.get("headers", [])
        if not isinstance(headers, list) or not self.matches(headers, fragment):
            return None

        column_map = self.map_columns(headers)
        normalized_rows = self._normalized_rows(fragment)
        mapped_rows = [self.parse_row(row, column_map) for row in normalized_rows]

        return {
            "table_type": self.table_type,
            "domain_column_map": column_map,
            "missing_columns_policy": self.missing_columns_policy,
            "extra_columns_policy": self.extra_columns_policy,
            "domain_rows": mapped_rows,
        }

    def transformer(self) -> WikiTablePayloadTransformer:
        return WikiTablePayloadTransformer(self)

    def collector(self) -> WikiTablePayloadCollector:
        return WikiTablePayloadCollector(self.table_type)

    # Legacy adapters
    def apply_to_payload(self, payload: dict[str, Any]) -> None:
        self.transformer().transform(payload)

    def parse_group(self, payload: Any) -> list[dict[str, Any]]:
        return self.collector().collect(payload)

    @staticmethod
    def _normalized_rows(table_data: dict[str, Any]) -> list[dict[str, Any]]:
        rich_rows = table_data.get("rich_rows", [])
        if isinstance(rich_rows, list) and rich_rows:
            return [row for row in rich_rows if isinstance(row, dict)]

        rows = table_data.get("rows", [])
        if isinstance(rows, list):
            dict_rows = [row for row in rows if isinstance(row, dict)]
            if dict_rows:
                return dict_rows

        raw_rows = table_data.get("raw_rows", [])
        if isinstance(raw_rows, list):
            return [row for row in raw_rows if isinstance(row, dict)]

        return []

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        """Czy parser pasuje do konkretnej tabeli."""
        del table_data
        header_set = set(headers)
        return all(bool(header_set & group) for group in self.required_header_groups)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        """Mapuje nagłówki tabeli na pola domenowe."""
        return {
            header: self.column_mapping[header]
            for header in headers
            if header in self.column_mapping
        }

    def parse_row(
        self,
        row: dict[str, Any],
        column_map: dict[str, str],
    ) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for header, value in row.items():
            key = column_map.get(header)
            if key:
                mapped[key] = value
        return mapped

    collect_rows = parse_group


__all__ = [
    "AbstractTableFragmentParser",
    "TableFragmentParserProtocol",
    "WikiTableBaseParser",
    "WikiTablePayloadCollector",
    "WikiTablePayloadTransformer",
]
