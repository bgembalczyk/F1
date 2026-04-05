from __future__ import annotations

import re
from typing import Any

from models.services import parse_seasons
from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.points.constants import POINTS_SCORING_HISTORY_EXPECTED_HEADERS
from scrapers.points.constants import SHORTENED_RACE_EXPECTED_HEADERS
from scrapers.points.constants import SPRINT_POSITIONS
from scrapers.points.constants import SPRINT_QUALIFYING_EXPECTED_HEADERS
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_section import SubSubSectionParser


class PointsScoringSystemsHistoryTableParser(WikiTableBaseParser):
    table_type = "points_scoring_systems_history"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _HEADER_ALIASES: dict[str, set[str]] = {
        "Seasons": {
            "Seasons",
            "Season(s)",
        },
        "Towards WDC": {
            "Towards WDC",
            "Drivers' Championship",
            "World Drivers' Championship",
            "WDC",
        },
        "Towards WCC": {
            "Towards WCC",
            "Constructors' Championship",
            "World Constructors' Championship",
            "WCC",
        },
    }

    @classmethod
    def _normalize_header(cls, value: str) -> str:
        compact = re.sub(r"\s+", " ", value).strip().lower()
        return compact.replace("\u2019", "'")

    @classmethod
    def _candidate_headers(cls, header: str) -> set[str]:
        aliases = cls._HEADER_ALIASES.get(header, {header})
        return {cls._normalize_header(alias) for alias in aliases}

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        normalized_headers = {self._normalize_header(header) for header in headers}
        return all(
            bool(self._candidate_headers(expected) & normalized_headers)
            for expected in POINTS_SCORING_HISTORY_EXPECTED_HEADERS
        )

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        column_map = {header: header.lower().replace(" ", "_") for header in headers}
        for header in headers:
            normalized = self._normalize_header(header)
            if normalized in self._candidate_headers("Towards WDC"):
                column_map[header] = "towards_wdc"
            elif normalized in self._candidate_headers("Towards WCC"):
                column_map[header] = "towards_wcc"
        return column_map


_SPRINT_DISQUALIFYING_HEADERS: frozenset[str] = frozenset(
    re.sub(r"[^a-z0-9]+", "", h.lower())
    for h in ("9th", "10th", "Fastest lap", "Race length completed")
)

_SPRINT_POSITION_KEYS: frozenset[str] = frozenset(
    pos.lower() for pos in SPRINT_POSITIONS
)


class SprintPointsTableParser(WikiTableBaseParser):
    table_type = "points_sprint_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        normalized_headers = {_normalize_header(header) for header in headers}
        expected = {
            _normalize_header(header) for header in SPRINT_QUALIFYING_EXPECTED_HEADERS
        }
        if _SPRINT_DISQUALIFYING_HEADERS & normalized_headers:
            return False
        return expected.issubset(normalized_headers)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        expected_lookup = _build_expected_header_lookup(
            SPRINT_QUALIFYING_EXPECTED_HEADERS,
        )
        return {
            header: expected_lookup.get(
                _normalize_header(header),
                _normalize_column_name(header),
            )
            for header in headers
        }

    def parse(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        result = super().parse(table_data)
        if result is None:
            return None
        result["domain_rows"] = [
            self._apply_schema_transforms(row) for row in result["domain_rows"]
        ]
        return result

    @staticmethod
    def _apply_schema_transforms(row: dict[str, Any]) -> dict[str, Any]:
        transformed: dict[str, Any] = {}
        for key, value in row.items():
            text = value if isinstance(value, str) else ""
            if key == "seasons":
                transformed[key] = [s.to_dict() for s in parse_seasons(text)]
            elif key in _SPRINT_POSITION_KEYS:
                transformed[key] = parse_int_from_text(text)
            else:
                transformed[key] = value
        return transformed


class ShortenedRacesPointsTableParser(WikiTableBaseParser):
    table_type = "points_shortened_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        normalized_headers = {_normalize_header(header) for header in headers}
        expected = {
            _normalize_header(header) for header in SHORTENED_RACE_EXPECTED_HEADERS
        }
        return expected.issubset(normalized_headers)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        expected_lookup = _build_expected_header_lookup(
            SHORTENED_RACE_EXPECTED_HEADERS,
        )
        return {
            header: expected_lookup.get(
                _normalize_header(header),
                _normalize_column_name(header),
            )
            for header in headers
        }

    def parse(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        result = super().parse(table_data)
        if result is None:
            return None
        result["domain_rows"] = self._group_rows_by_seasons(result["domain_rows"])
        return result

    @staticmethod
    def _group_rows_by_seasons(
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        order: list[str] = []
        for row in rows:
            seasons_text = row.get("seasons") or ""
            if seasons_text not in groups:
                groups[seasons_text] = []
                order.append(seasons_text)
            race_length_entry = {
                k: v for k, v in row.items() if k not in ("seasons", "notes")
            }
            groups[seasons_text].append(race_length_entry)
        return [
            {
                "seasons": [s.to_dict() for s in parse_seasons(seasons_text)],
                "race_length_points": groups[seasons_text],
            }
            for seasons_text in order
        ]


def _normalize_header(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", header.lower())


def _normalize_column_name(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", header.lower()).strip("_")


def _build_expected_header_lookup(expected_headers: list[str]) -> dict[str, str]:
    return {
        _normalize_header(header): _normalize_column_name(header)
        for header in expected_headers
    }


class SprintRacesSubSubSectionParser(SubSubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = SprintPointsTableParser()

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        if not parsed.get("sub_sub_sub_sections"):
            parsed = self.child_parser.parse_group(elements, context=context)
        self.apply_table_parser(parsed)
        return parsed

    def apply_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self.apply_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.apply_table_parser(item)

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

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self.apply_table_parser(parsed)
        return parsed

    def apply_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self.apply_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.apply_table_parser(item)

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
        parsed = super().parse_group(elements, context=context)
        self.sprint_parser.apply_table_parser(parsed)
        self.shortened_parser.apply_table_parser(parsed)
        return parsed


class SpecialCasesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = _SpecialCasesSubSubSectionRouter()


class PointsScoringSystemsSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = SpecialCasesSubSectionParser()
        self._table_parser = PointsScoringSystemsHistoryTableParser()

    @property
    def sprint_subsection_parser(self) -> SprintRacesSubSubSectionParser:
        router = self.child_parser.child_parser  # type: ignore[union-attr]
        return router.sprint_parser  # type: ignore[union-attr]

    @property
    def shortened_subsection_parser(self) -> ShortenedRacesSubSubSectionParser:
        router = self.child_parser.child_parser  # type: ignore[union-attr]
        return router.shortened_parser  # type: ignore[union-attr]

    def collect_rows(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return self._table_parser.collect_rows(parsed)

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self.apply_table_parser(parsed)
        return parsed

    def apply_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self.apply_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.apply_table_parser(item)

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
