import re
from typing import Any

from models.services.season import parse_seasons
from scrapers.constants_points import POINTS_NOTES_HEADER
from scrapers.constants_points import POINTS_SCORING_HISTORY_EXPECTED_HEADERS
from scrapers.constants_points import ROLE_PATTERN
from scrapers.helpers.parsing import parse_int_from_text
from scrapers.points_constant import HISTORY_POSITION_KEYS_WITH_FASTEST_LAP
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper
from scrapers.points_constant import HISTORY_POSITION_KEYS_WITH_FASTEST_LAP
from scrapers.wiki_table_base_mapper import WikiTableBaseMapper


class PointsScoringSystemsHistoryTableMapper(WikiTableBaseMapper):
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
        column_map: dict[str, str] = {}
        for header in headers:
            normalized = self._normalize_header(header)
            if normalized in self._candidate_headers("Towards WDC"):
                column_map[header] = "drivers_championship"
            elif normalized in self._candidate_headers("Towards WCC"):
                column_map[header] = "constructors_championship"
            elif normalized == self._normalize_header(POINTS_NOTES_HEADER):
                pass  # skip the Notes column
            else:
                column_map[header] = header.lower().replace(" ", "_")
        return column_map

    def map(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        result = super().map(table_data)
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
            text = (
                value.get("text", "")
                if isinstance(value, dict)
                else (value if isinstance(value, str) else "")
            )
            if key == "seasons":
                transformed[key] = [s.to_dict() for s in parse_seasons(text)]
            elif key == "1st":
                int_val = parse_int_from_text(text)
                if int_val is None:
                    transformed[key] = None
                else:
                    role_match = ROLE_PATTERN.search(text)
                    if role_match:
                        role = (
                            "driver"
                            if role_match.group(1).lower() == "d"
                            else "constructor"
                        )
                        transformed[key] = {"value": int_val, "role": role}
                    else:
                        transformed[key] = int_val
            elif key in HISTORY_POSITION_KEYS_WITH_FASTEST_LAP:
                transformed[key] = parse_int_from_text(text)
            else:
                transformed[key] = value
        return transformed

