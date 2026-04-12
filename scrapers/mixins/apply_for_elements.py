"""Mixin for applying table parser to generic structured elements."""

from typing import Any

from scrapers.protocols.has_table_parser import HasTableParserABC


class ApplyForElementsMixin:
    """Mixin to apply a table parser to elements within a structured payload."""

    def apply_table_parser(self: HasTableParserABC, payload: dict[str, Any]) -> None:
        """Recursively applies the table parser to nested dictionaries."""
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self.apply_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.apply_table_parser(item)

    def _apply_for_elements(
        self: HasTableParserABC,
        elements: list[dict[str, Any]],
    ) -> None:
        """Applies the table parser to a list of elements."""
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.map(data)
            if parsed is not None:
                element["data"] = parsed
