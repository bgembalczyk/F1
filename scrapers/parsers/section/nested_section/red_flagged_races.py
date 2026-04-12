import json
from typing import Any

from scrapers.parsers.section.nested_section.base import NestedWikiSectionParser
from scrapers.parsers.section.sub_section.non_championships_races import NonChampionshipsRacesSubSectionParser
from scrapers.world_championships_races_table_mapper import WorldChampionshipsRacesTableMapper


class RedFlaggedRacesSectionParser(NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = NonChampionshipsRacesSubSectionParser()
        self._world_championship_table_mapper = WorldChampionshipsRacesTableMapper()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._world_championship_table_mapper.apply_to_payload(parsed)
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
