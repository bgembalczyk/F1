from __future__ import annotations

from abc import ABC
from typing import Any

from bs4 import Tag

from scrapers.parsers.mixins.wiki.table_payload.collect import WikiTablePayloadCollectMixin
from scrapers.parsers.mixins.wiki.table_payload.transform import WikiTablePayloadTransformMixin
from scrapers.parsers.contracts.constants_mapping_contracts import GroupParsingMixin
from scrapers.parsers.contracts.constants_mapping_contracts import MatchesMixin
from scrapers.parsers.contracts.constants_mapping_contracts import RowMappingMixin
from scrapers.parsers.contracts.constants_mapping_contracts import TableDomainMapperABC
from scrapers.parsers.contracts.html import TagParserABC


class WikiTableBaseParser(TagParserABC[dict[str, Any]], ABC):
    """Bazowa klasa parserów tabel wiki (HTML Tag -> parsed data)."""

    def parse(self, raw: Tag) -> dict[str, Any]:
        raise NotImplementedError


class WikiTableBaseMapper(
    TableDomainMapperABC,
    MatchesMixin,
    RowMappingMixin[dict[str, Any], dict[str, Any]],
    GroupParsingMixin[Any, dict[str, Any]],
    WikiTablePayloadTransformMixin,
    WikiTablePayloadCollectMixin,
    ABC,
):
    """Bazowa klasa runtime dla mapperów fragmentów tabel Wikipedii."""

    table_type: str = "wiki_table"
    missing_columns_policy: str = "skip"
    extra_columns_policy: str = "ignore"
    required_header_groups: tuple[frozenset[str], ...] = ()
    column_mapping: dict[str, str] = {}

    def map(self, fragment: dict[str, Any]) -> dict[str, Any] | None:
        return self.map_fragment(fragment)

    def map_fragment(self, fragment: dict[str, Any]) -> dict[str, Any] | None:
        headers = fragment.get("headers", [])
        if not isinstance(headers, list) or not self.matches(headers, fragment):
            return None

        column_map = self.map_columns(headers)
        normalized_rows = self._normalized_rows(fragment)
        mapped_rows = [self.parse_row(row, column_map) for row in normalized_rows]

        return {
            "table_type": self.table_type,
            "domain_column_map": column_map,
            "missing_columns_policy": self.missing_columns_policy,
            "extra_columns_policy": self.extra_columns_policy,
            "domain_rows": mapped_rows,
        }

    def apply_to_payload(self, payload: dict[str, Any]) -> None:
        self.transform(payload)

    def parse_group(self, payload: Any) -> list[dict[str, Any]]:
        return self.collect(payload)

    def map_table(self, table: Any) -> list[dict[str, Any]]:
        return self.parse_group(table)

    @staticmethod
    def _normalized_rows(table_data: dict[str, Any]) -> list[dict[str, Any]]:
        rich_rows = table_data.get("rich_rows", [])
        if isinstance(rich_rows, list) and rich_rows:
            return [row for row in rich_rows if isinstance(row, dict)]

        rows = table_data.get("rows", [])
        if isinstance(rows, list):
            dict_rows = [row for row in rows if isinstance(row, dict)]
            if dict_rows:
                return dict_rows

        raw_rows = table_data.get("raw_rows", [])
        if isinstance(raw_rows, list):
            return [row for row in raw_rows if isinstance(row, dict)]

        return []

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        header_set = set(headers)
        return all(bool(header_set & group) for group in self.required_header_groups)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self.column_mapping[header]
            for header in headers
            if header in self.column_mapping
        }

    def parse_row(
        self,
        row: dict[str, Any],
        column_map: dict[str, str],
    ) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for header, value in row.items():
            key = column_map.get(header)
            if key:
                mapped[key] = value
        return mapped

    def map_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return self.parse_row(row, self.map_columns(list(row.keys())))

    collect_rows = parse_group


TableFragmentParserABC = WikiTableBaseParser
WikiTableFragmentParser = WikiTableBaseParser


__all__ = [
    "WikiTableBaseParser",
    "WikiTableBaseMapper",
]
