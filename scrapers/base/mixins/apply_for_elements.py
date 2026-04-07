from typing import Any, Protocol

class SupportsTableParser(Protocol):
    _table_parser: Any

class ApplyForElementsMixin(SupportsTableParser):
    def _apply_table_parser_to_sections(self, payload: dict[str, Any], section_key: str) -> None:
        for section in payload.get(section_key, []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_table_parser_to_sections(section, section_key)

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
