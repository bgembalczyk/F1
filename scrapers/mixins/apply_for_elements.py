"""Mixin for applying table parser to generic structured elements."""

from typing import Any
from typing import Protocol
from typing import runtime_checkable


@runtime_checkable
class _HasTableParser(Protocol):
    _table_parser: Any


@runtime_checkable
class _HasTableMapper(Protocol):
    _table_mapper: Any


class ApplyForElementsMixin:
    """Mixin to apply a table parser to elements within a structured payload."""

    def apply_table_mapper(self: _HasTableMapper, payload: dict[str, Any]) -> None:
        """Recursively applies the table mapper to nested dictionaries."""
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self.apply_table_mapper(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.apply_table_mapper(item)

    def _apply_for_elements(
        self: _HasTableParser,
        elements: list[dict[str, Any]],
    ) -> None:
        """Applies the table parser to a list of elements."""
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            mapper = getattr(self, "_table_mapper", None)
            if mapper is None:
                mapper = self._table_parser
            parsed = mapper.map(data)
            if parsed is not None:
                element["data"] = parsed
