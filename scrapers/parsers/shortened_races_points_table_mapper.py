from typing import Any

from models.services.season import parse_seasons
from scrapers.constants_points import SHORTENED_RACE_EXPECTED_HEADERS
from scrapers.parsers.wiki.points_helpers import build_expected_header_lookup
from scrapers.parsers.wiki.points_helpers import normalize_column_name
from scrapers.parsers.wiki.points_helpers import normalize_header
from scrapers.parsers.wiki_table_base_mapper import WikiTableBaseMapper


class ShortenedRacesPointsTableMapper(WikiTableBaseMapper):
    table_type = "points_shortened_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        normalized_headers = {normalize_header(header) for header in headers}
        expected = {
            normalize_header(header) for header in SHORTENED_RACE_EXPECTED_HEADERS
        }
        return expected.issubset(normalized_headers)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        expected_lookup = build_expected_header_lookup(
            SHORTENED_RACE_EXPECTED_HEADERS,
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
            if isinstance(seasons_text, dict):
                seasons_text = seasons_text.get("text", "")
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

