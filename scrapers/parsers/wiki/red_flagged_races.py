from __future__ import annotations

import json
from typing import Any

from bs4 import Tag

from scrapers.parsers.table.red_flagged_races import NonChampionshipsRacesTableMapper
from scrapers.parsers.table.red_flagged_races import WorldChampionshipsRacesTableMapper
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser
from scrapers.parsers.wiki.sublevels.sub_section import SubSectionParser
from scrapers.parsers.wiki.sublevels.sub_sub_sub_section import SubSubSubSectionParser


class NonChampionshipsRacesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = NonChampionshipsRacesTableMapper()
        self._fallback_element_parser = SubSubSubSectionParser()

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
        self._table_parser.apply_to_payload(parsed)
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


class RedFlaggedRacesSectionParser(NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = NonChampionshipsRacesSubSectionParser()
        self._world_championship_table_parser = WorldChampionshipsRacesTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._world_championship_table_parser.apply_to_payload(parsed)
        return parsed

    @staticmethod
    def collect_rows(
        payload: dict[str, Any],
        *,
        table_type: str,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []

        def visit(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("table_type") == table_type:
                    table_rows = node.get("domain_rows", [])
                    if isinstance(table_rows, list):
                        rows.extend(
                            [row for row in table_rows if isinstance(row, dict)],
                        )
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for item in node:
                    visit(item)

        visit(payload)
        deduplicated: list[dict[str, Any]] = []
        seen: set[str] = set()
        for row in rows:
            signature = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if signature in seen:
                continue
            seen.add(signature)
            deduplicated.append(row)
        return deduplicated
