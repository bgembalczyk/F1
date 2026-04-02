from __future__ import annotations

from typing import Any

from scrapers.points.constants import POINTS_SCORING_HISTORY_EXPECTED_HEADERS
from scrapers.points.constants import SHORTENED_RACE_EXPECTED_HEADERS
from scrapers.points.constants import SPRINT_QUALIFYING_EXPECTED_HEADERS
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser


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


class _SpecialCasesSubSubSectionRouter(SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.sprint_parser = SprintRacesSubSubSectionParser()
        self.shortened_parser = ShortenedRacesSubSubSectionParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        section_id = getattr(context, "section_id", "") or ""
        if "sprint" in section_id.lower():
            return self.sprint_parser.parse_group(elements, context=context)
        if "shortened" in section_id.lower():
            return self.shortened_parser.parse_group(elements, context=context)
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
