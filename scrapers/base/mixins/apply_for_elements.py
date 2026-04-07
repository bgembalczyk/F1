from typing import Any, Protocol

class SupportsTableParser(Protocol):
    _table_parser: Any

class ApplyForElementsMixin(SupportsTableParser):
    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed
