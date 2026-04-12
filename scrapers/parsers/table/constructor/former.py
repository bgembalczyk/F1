from typing import Any

from scrapers.constants.shared_headers import SHARED_SEASONS_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_NAME_HEADER
from scrapers.parsers.wiki.tables.base_mapper import WikiTableBaseParser


class FormerConstructorsTableParser(WikiTableBaseParser):
    table_type = "former_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        expected = {
            CONSTRUCTOR_NAME_HEADER.lower(),
            CONSTRUCTOR_LICENSED_IN_HEADER.lower(),
            SHARED_SEASONS_HEADER.lower(),
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.strip().lower().replace(" ", "_") for header in headers}

    def parse_row(
        self,
        row: dict[str, Any],
        column_map: dict[str, str],
    ) -> dict[str, Any]:
        mapped = super().parse_row(row, column_map)
        normalized = dict(mapped)
        constructor = normalized.pop("constructor", None)
        if constructor is not None:
            normalized["chassis_constructor"] = constructor
        return normalized
