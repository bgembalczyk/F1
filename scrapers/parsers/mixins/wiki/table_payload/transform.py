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
