from __future__ import annotations

import json
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.source_catalog import RED_FLAGGED_RACES
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.grands_prix.red_flagged_races_scraper.base import (
    RedFlaggedRacesBaseScraper,
)
from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import SubSubSubSectionParser

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions


class WorldChampionshipsRacesTableParser(WikiTableBaseParser):
    table_type = "red_flagged_world_championship_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Year": "season",
        "Grand Prix": "grand_prix",
        "Lap": "lap",
        "R": "restart_status",
        "Winner": "winner",
        "Incident that prompted red flag": "incident",
        "Failed to make the restart - Drivers": "failed_to_make_restart_drivers",
        "Failed to make the restart - Reason": "failed_to_make_restart_reason",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        }
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


class NonChampionshipsRacesTableParser(WikiTableBaseParser):
    table_type = "red_flagged_non_championship_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Year": "season",
        "Event": "event",
        "Lap": "lap",
        "R": "restart_status",
        "Winner": "winner",
        "Incident that prompted red flag": "incident",
        "Failed to make the restart - Drivers": "failed_to_make_restart_drivers",
        "Failed to make the restart - Reason": "failed_to_make_restart_reason",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {
            "Year",
            "Event",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        }
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


class NonChampionshipsRacesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = NonChampionshipsRacesTableParser()
        self._fallback_element_parser = SubSubSubSectionParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        if not self._contains_table_elements(parsed):
            parsed["elements"] = self._fallback_element_parser.parse_group(
                elements,
                context=context,
            ).get("elements", [])
        parsed.setdefault("elements", [])
        self._merge_unique_table_elements(
            parsed["elements"],
            self._extract_descendant_table_elements(elements),
        )
        self._apply_non_championship_table_parser(parsed)
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
                parsed = self._fallback_element_parser.parse_group([table]).get(
                    "elements",
                    [],
                )
                for parsed_element in parsed:
                    if (
                        isinstance(parsed_element, dict)
                        and parsed_element.get("kind") == "table"
                    ):
                        table_elements.append(parsed_element)
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

    def _apply_non_championship_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_non_championship_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_non_championship_table_parser(item)

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


class RedFlaggedRacesSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = NonChampionshipsRacesSubSectionParser()
        self._world_championship_table_parser = WorldChampionshipsRacesTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_world_championship_table_parser(parsed)
        return parsed

    def _apply_world_championship_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_world_championship_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_world_championship_table_parser(item)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._world_championship_table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed


class RedFlaggedRacesScraper(RedFlaggedRacesBaseScraper):
    """Composite scraper returning world and non-championship red-flagged races."""

    _SUPPORTED_EXPORT_SCOPES = {"all", "world_championship", "non_championship"}
    _SCHEMA_COLUMNS = RedFlaggedRacesBaseScraper.build_common_red_flag_columns()
    _SCHEMA_COLUMNS[1] = column("Grand Prix", "grand_prix", UrlColumn())

    CONFIG = build_scraper_config(
        url=RED_FLAGGED_RACES.base_url,
        section_id=RED_FLAGGED_RACES.section_id,
        expected_headers=[
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        ],
        schema=TableSchemaDSL(
            columns=_SCHEMA_COLUMNS,
        ),
        record_factory=RECORD_FACTORIES.mapping(),
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        export_scope: str = "all",
    ) -> None:
        super().__init__(options=options)
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = (
                f"Unsupported export_scope='{export_scope}' for "
                f"{self.__class__.__name__}"
            )
            raise ValueError(msg)
        self._export_scope = export_scope
        parser = RedFlaggedRacesSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        body_content = BodyContentParser.find_body_content(soup)
        parsed = self.body_content_parser.parse(body_content) if body_content else {}
        world_records = self._collect_table_rows(
            parsed,
            table_type="red_flagged_world_championship_races",
        )
        non_championship_records = self._collect_table_rows(
            parsed,
            table_type="red_flagged_non_championship_races",
        )
        if self._export_scope == "world_championship":
            return world_records
        if self._export_scope == "non_championship":
            return non_championship_records
        return [*world_records, *non_championship_records]

    def _collect_table_rows(
        self,
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
