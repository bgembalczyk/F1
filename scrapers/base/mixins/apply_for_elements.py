"""Mixin for applying table parser to generic structured elements."""

from typing import Any
from typing import Protocol

class _HasTableParser(Protocol):
    _table_parser: Any

class ApplyForElementsMixin:
    """Mixin to apply a table parser to elements within a structured payload."""

    def apply_table_parser(self: _HasTableParser, obj: dict[str, Any]) -> None:
        """Recursively apply table parser to all section elements in a dictionary."""
        for key, value in obj.items():
            if key == "elements" and isinstance(value, list):
                self._apply_for_elements(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.apply_table_parser(item)

    def _apply_for_elements(
        self: _HasTableParser, elements: list[dict[str, Any]]
    ) -> None:
        """Applies the table parser to a list of elements."""
        for element in elements:
            if element.get("kind") != "table":
                continue
            table_data = element.get("data")
            if not isinstance(table_data, dict):
                continue
            parsed_data = self._table_parser.parse(table_data)
            if parsed_data is not None:
                element["data"] = parsed_data
