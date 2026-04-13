from typing import Any

from models.services.season import parse_seasons
from scrapers.constants.constants_points import SPRINT_QUALIFYING_EXPECTED_HEADERS
from scrapers.helpers.parsing import parse_int_from_text
from scrapers.points_constant import SPRINT_DISQUALIFYING_HEADERS
from scrapers.points_constant import SPRINT_POSITION_KEYS
from scrapers.points_helpers import build_expected_header_lookup
from scrapers.points_helpers import normalize_column_name
from scrapers.points_helpers import normalize_header
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper


class SprintPointsTableMapper(WikiTableBaseMapper):
    table_type = "points_sprint_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        normalized_headers = {normalize_header(header) for header in headers}
        expected = {
            normalize_header(header) for header in SPRINT_QUALIFYING_EXPECTED_HEADERS
        }
        if SPRINT_DISQUALIFYING_HEADERS & normalized_headers:
            return False
        return expected.issubset(normalized_headers)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        expected_lookup = build_expected_header_lookup(
            SPRINT_QUALIFYING_EXPECTED_HEADERS,
        )
        return {
            header: expected_lookup.get(
                normalize_header(header),
                normalize_column_name(header),
            )
            for header in headers
        }

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
            elif key in SPRINT_POSITION_KEYS:
                transformed[key] = parse_int_from_text(text)
            else:
                transformed[key] = value
        return transformed

