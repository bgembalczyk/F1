from __future__ import annotations

from typing import Any


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
