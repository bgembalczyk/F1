from __future__ import annotations

import logging
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.options import ScraperOptions
from scrapers.base.source_catalog import RED_FLAGGED_RACES
from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.grands_prix.red_flagged_races_scraper.base import RedFlaggedRacesBaseScraper
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import SubSubSubSectionParser

logger = logging.getLogger(__name__)


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
        self._fallback_parser = SubSubSubSectionParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        logger.debug(
            "[non_champ_subsection] parse_group start: elements=%d",
            len(elements),
        )
        parsed = super().parse_group(elements, context=context)
        if not self._has_table_payload(parsed):
            logger.debug(
                "[non_champ_subsection] no table payload in nested structure -> using fallback parser",
            )
            parsed["elements"] = self._fallback_parser.parse_group(
                elements,
                context=context,
            )["elements"]
        else:
            logger.debug(
                "[non_champ_subsection] table payload found in nested structure",
            )
        self._apply_non_championship_table_parser(parsed)
        logger.debug("[non_champ_subsection] parse_group end")
        return parsed

    def _has_table_payload(self, payload: Any) -> bool:
        if isinstance(payload, dict):
            if payload.get("kind") == "table":
                return True
            return any(self._has_table_payload(value) for value in payload.values())
        if isinstance(payload, list):
            return any(self._has_table_payload(item) for item in payload)
        return False

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
        self._fallback_parser = SubSubSubSectionParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        logger.debug(
            "[red_flag_section] parse_group start: elements=%d",
            len(elements),
        )
        parsed = super().parse_group(elements, context=context)
        if not self._has_table_payload(parsed):
            logger.debug(
                "[red_flag_section] no table payload in nested structure -> using fallback parser",
            )
            parsed["elements"] = self._fallback_parser.parse_group(
                elements,
                context=context,
            )["elements"]
        else:
            logger.debug("[red_flag_section] table payload found in nested structure")
        self._apply_world_championship_table_parser(parsed)
        logger.debug("[red_flag_section] parse_group end")
        return parsed

    def _has_table_payload(self, payload: Any) -> bool:
        if isinstance(payload, dict):
            if payload.get("kind") == "table":
                return True
            return any(self._has_table_payload(value) for value in payload.values())
        if isinstance(payload, list):
            return any(self._has_table_payload(item) for item in payload)
        return False

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
    """Composite scraper that returns both world and non-championship red-flagged races."""

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
            msg = f"Unsupported export_scope='{export_scope}' for {self.__class__.__name__}"
            raise ValueError(msg)
        self._export_scope = export_scope
        parser = RedFlaggedRacesSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        logger.info(
            "[red_flag_scraper] start parse soup export_scope=%s",
            self._export_scope,
        )
        parsed = self._parse_document_structure(soup)
        world_records = self._collect_table_rows(
            parsed,
            table_type="red_flagged_world_championship_races",
        )
        non_championship_records = self._collect_table_rows(
            parsed,
            table_type="red_flagged_non_championship_races",
        )
        if self._export_scope == "world_championship":
            logger.info(
                "[red_flag_scraper] parsed world_championship records=%d",
                len(world_records),
            )
            return world_records
        if self._export_scope == "non_championship":
            logger.info(
                "[red_flag_scraper] parsed non_championship records=%d",
                len(non_championship_records),
            )
            return non_championship_records
        logger.info(
            "[red_flag_scraper] parsed all records world=%d non_championship=%d total=%d",
            len(world_records),
            len(non_championship_records),
            len(world_records) + len(non_championship_records),
        )
        return [*world_records, *non_championship_records]

    def _parse_document_structure(self, soup: BeautifulSoup) -> dict[str, Any]:
        body_content = BodyContentParser.find_body_content(soup)
        if body_content:
            logger.debug("[red_flag_scraper] using bodyContent parser branch")
            return self.body_content_parser.parse(body_content)

        content_text = soup.find(
            "div",
            id=lambda x: x and "content-text" in x,
            class_=lambda x: x
            and any(
                "body-content" in token
                for token in (x if isinstance(x, list) else x.split())
            ),
        )
        if not isinstance(content_text, Tag):
            logger.debug(
                "[red_flag_scraper] content-text branch not found, trying mw-content-ltr",
            )
            content_text = soup.find(
                "div",
                class_=lambda x: x
                and "mw-content-ltr" in (x if isinstance(x, list) else x.split()),
            )
        if isinstance(content_text, Tag):
            logger.debug("[red_flag_scraper] using content_text parser branch")
            return {
                "content_text": self.body_content_parser.content_text_parser.parse(
                    content_text,
                ),
            }

        fallback_root = soup.find("body")
        if not isinstance(fallback_root, Tag):
            logger.debug(
                "[red_flag_scraper] body fallback missing, trying html fallback",
            )
            fallback_root = soup.find("html")
        if not isinstance(fallback_root, Tag):
            logger.warning(
                "[red_flag_scraper] could not find body/html fallback root; returning empty sections",
            )
            return {"content_text": {"sections": []}}
        logger.debug("[red_flag_scraper] using body/html fallback parser branch")
        return {
            "content_text": self.body_content_parser.content_text_parser.parse(
                fallback_root,
            ),
        }

    def _collect_table_rows(
        self,
        payload: dict[str, Any],
        *,
        table_type: str,
    ) -> list[dict[str, Any]]:
        logger.debug(
            "[red_flag_scraper] collecting rows table_type=%s",
            table_type,
        )
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
        logger.debug(
            "[red_flag_scraper] collected rows table_type=%s count=%d",
            table_type,
            len(rows),
        )
        return rows
