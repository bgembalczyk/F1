from __future__ import annotations

import logging
from typing import Any

from bs4 import Tag

from scrapers.points.constants import POINTS_SCORING_HISTORY_EXPECTED_HEADERS
from scrapers.points.constants import SHORTENED_RACE_EXPECTED_HEADERS
from scrapers.points.constants import SPRINT_QUALIFYING_EXPECTED_HEADERS
from scrapers.wiki.parsers.elements.table import TableParser
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser

logger = logging.getLogger(__name__)


def _trace(message: str) -> None:
    # Intentionally stdout-based to make diagnostics visible in list runs
    # even when Python logging is not configured.
    print(f"[points][shortened-debug] {message}")


class PointsScoringSystemsHistoryTableParser(WikiTableBaseParser):
    table_type = "points_scoring_systems_history"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        return set(POINTS_SCORING_HISTORY_EXPECTED_HEADERS).issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.lower().replace(" ", "_") for header in headers}


class SprintPointsTableParser(WikiTableBaseParser):
    table_type = "points_sprint_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        return set(SPRINT_QUALIFYING_EXPECTED_HEADERS).issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.lower().replace(" ", "_") for header in headers}


class ShortenedRacesPointsTableParser(WikiTableBaseParser):
    table_type = "points_shortened_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        return set(SHORTENED_RACE_EXPECTED_HEADERS).issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.lower().replace(" ", "_") for header in headers}


class SprintRacesSubSubSectionParser(SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = SprintPointsTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_table_parser(parsed)
        return parsed

    def _apply_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_table_parser(item)

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


class ShortenedRacesSubSubSectionParser(SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = ShortenedRacesPointsTableParser()
        self._raw_table_parser = TableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        context_section_id = (getattr(context, "section_id", "") or "")
        _trace(
            f"parse_group start: section_id={context_section_id!r} elements={len(elements)}",
        )
        logger.debug(
            "ShortenedRacesSubSubSectionParser.parse_group start: section_id=%s elements=%d",
            context_section_id,
            len(elements),
        )
        parsed = super().parse_group(elements, context=context)
        self._apply_table_parser(parsed)
        self._apply_shortened_section_fallback(
            parsed,
            elements,
            context_section_id=context_section_id,
        )
        logger.debug(
            "ShortenedRacesSubSubSectionParser.parse_group done: has_shortened_table=%s",
            self._contains_shortened_table(parsed),
        )
        _trace(
            f"parse_group done: section_id={context_section_id!r} has_shortened_table={self._contains_shortened_table(parsed)}",
        )
        return parsed

    def _apply_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_table_parser(item)

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
                logger.debug(
                    "ShortenedRacesSubSubSectionParser: mapped table from normal flow",
                )

    def _apply_shortened_section_fallback(
        self,
        payload: dict[str, Any],
        elements: list,
        *,
        context_section_id: str,
    ) -> None:
        if context_section_id.lower() != "shortened_races":
            _trace(
                f"fallback skipped: section_id={context_section_id!r} (expected 'Shortened_races')",
            )
            logger.debug(
                "Shortened fallback skipped: section_id=%s (expected Shortened_races)",
                context_section_id,
            )
            return
        if self._contains_shortened_table(payload):
            _trace("fallback skipped: shortened table already present in payload")
            logger.debug("Shortened fallback skipped: table already present in payload")
            return

        fallback_tables = self._extract_shortened_tables(elements)
        if not fallback_tables:
            _trace("fallback scan finished: no matching wikitable found")
            logger.debug("Shortened fallback: no matching wikitable found")
            return

        target = payload.setdefault("elements", [])
        if not isinstance(target, list):
            _trace(
                f"fallback aborted: payload['elements'] has invalid type={type(target).__name__}",
            )
            logger.debug(
                "Shortened fallback aborted: payload['elements'] is not a list (%s)",
                type(target).__name__,
            )
            return
        target.extend(
            [
                {
                    "kind": "table",
                    "type": "table",
                    "source_section_id": context_section_id,
                    "data": table_payload,
                }
                for table_payload in fallback_tables
            ],
        )
        logger.info(
            "Shortened fallback attached %d mapped table(s) for section_id=%s",
            len(fallback_tables),
            context_section_id,
        )
        _trace(
            f"fallback attached tables: count={len(fallback_tables)} section_id={context_section_id!r}",
        )

    def _contains_shortened_table(self, payload: Any) -> bool:
        if isinstance(payload, dict):
            if payload.get("table_type") == "points_shortened_races":
                return True
            return any(self._contains_shortened_table(value) for value in payload.values())
        if isinstance(payload, list):
            return any(self._contains_shortened_table(item) for item in payload)
        return False

    def _extract_shortened_tables(self, elements: list) -> list[dict[str, Any]]:
        tables: list[dict[str, Any]] = []
        seen_ids: set[int] = set()
        scanned = 0
        for node in elements:
            if not isinstance(node, Tag):
                continue
            for table in node.find_all("table", class_="wikitable"):
                scanned += 1
                key = id(table)
                if key in seen_ids:
                    continue
                seen_ids.add(key)
                raw_data = self._raw_table_parser.parse(table)
                mapped = self._table_parser.parse(raw_data)
                if mapped is not None:
                    tables.append(mapped)
        logger.debug(
            "Shortened fallback scan summary: scanned_tables=%d matched_tables=%d",
            scanned,
            len(tables),
        )
        _trace(
            f"fallback scan summary: scanned_tables={scanned} matched_tables={len(tables)}",
        )
        return tables


class _SpecialCasesSubSubSectionRouter(SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.sprint_parser = SprintRacesSubSubSectionParser()
        self.shortened_parser = ShortenedRacesSubSubSectionParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        section_id = getattr(context, "section_id", "") or ""
        _trace(
            f"router decision: section_id={section_id!r} elements={len(elements)}",
        )
        logger.debug(
            "SpecialCases router: section_id=%s elements=%d",
            section_id,
            len(elements),
        )
        if "sprint" in section_id.lower():
            _trace("router -> sprint_parser")
            logger.debug("SpecialCases router -> sprint_parser")
            return self.sprint_parser.parse_group(elements, context=context)
        if "shortened" in section_id.lower():
            _trace("router -> shortened_parser")
            logger.debug("SpecialCases router -> shortened_parser")
            return self.shortened_parser.parse_group(elements, context=context)
        _trace("router -> default SubSubSectionParser")
        logger.debug("SpecialCases router -> default SubSubSectionParser")
        return super().parse_group(elements, context=context)


class SpecialCasesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = _SpecialCasesSubSubSectionRouter()


class PointsScoringSystemsSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSectionParser()
        self._table_parser = PointsScoringSystemsHistoryTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_table_parser(parsed)
        return parsed

    def _apply_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_table_parser(item)

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
