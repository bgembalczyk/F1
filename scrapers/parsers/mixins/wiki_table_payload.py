from __future__ import annotations

from typing import Any


class WikiTablePayloadTransformMixin:
    """Traverse parsed payload trees and map wiki table elements."""

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
            parsed = self.parse(data)
            if parsed is not None:
                element["data"] = parsed


class WikiTablePayloadCollectMixin:
    """Collect domain rows from nested payload trees for parser's table type."""

    table_type: str

    def collect(self, payload_tree: Any) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        self._collect_from_node(payload_tree, rows)
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
