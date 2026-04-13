from typing import Any

from bs4 import Tag

from scrapers.mappers.non_championships_races_table_mapper import (
    NonChampionshipRacesTableMapper,
)
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.recursive import RecursiveSectionParser
from scrapers.parsers.wiki.sub_sub_sub_section import SubSubSubSectionParser


class NonChampionshipsRacesSubSectionParser(RecursiveSectionParser):
    heading_class = "mw-heading4"
    output_key = "sub_sub_sections"

    def __init__(self) -> None:
        super().__init__()
        self._table_mapper = NonChampionshipRacesTableMapper()
        self._fallback_element_parser = SubSubSubSectionParser()

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, object]:
        return super().parse(element, context=context)

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        if not self._contains_table_elements(parsed):
            parsed["elements"] = self._fallback_element_parser.parse(
                elements,
                context=context,
            ).get("elements", [])
        parsed.setdefault("elements", [])
        self._merge_unique_table_elements(
            parsed["elements"],
            self._extract_descendant_table_elements(elements),
        )
        self._table_mapper.apply_to_payload(parsed)
        return parsed

    def _contains_table_elements(self, payload: dict[str, Any]) -> bool:
        def visit(node: Any) -> bool:
            if isinstance(node, dict):
                if node.get("kind") == "table":
                    return True
                return any(visit(value) for value in node.values())
            if isinstance(node, list):
                return any(visit(item) for item in node)
            return False

        return visit(payload)

    def _extract_descendant_table_elements(
        self,
        elements: list,
    ) -> list[dict[str, Any]]:
        table_elements: list[dict[str, Any]] = []
        seen_table_ids: set[int] = set()
        for element in elements:
            if not isinstance(element, Tag):
                continue
            for table in element.find_all("table"):
                if id(table) in seen_table_ids:
                    continue
                seen_table_ids.add(id(table))
                parsed = self._fallback_element_parser.parse([table]).get(
                    "elements",
                    [],
                )
                table_elements.extend(
                    parsed_element
                    for parsed_element in parsed
                    if isinstance(parsed_element, dict)
                    and parsed_element.get("kind") == "table"
                )
        return table_elements

    def _merge_unique_table_elements(
        self,
        target: list[dict[str, Any]],
        additions: list[dict[str, Any]],
    ) -> None:
        existing_signatures = {
            self._table_signature(item)
            for item in target
            if item.get("kind") == "table"
        }
        for item in additions:
            signature = self._table_signature(item)
            if signature in existing_signatures:
                continue
            existing_signatures.add(signature)
            target.append(item)

    def _table_signature(self, element: dict[str, Any]) -> tuple[Any, ...]:
        data = element.get("data")
        if not isinstance(data, dict):
            return ("invalid",)
        headers = tuple(data.get("headers", []))
        rows = data.get("rows", [])
        rows_count = len(rows) if isinstance(rows, list) else -1
        return headers, rows_count
