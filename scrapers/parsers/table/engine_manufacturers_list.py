from typing import Any

from scrapers.parsers.wiki.tables.base_mapper import WikiTableBaseParser


class EngineManufacturersTableParser(WikiTableBaseParser):
    table_type = "engine_manufacturers_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Manufacturer": "engine_constructor",
        "Engines built in": "engines_built_in",
        "Seasons": "seasons",
        "Races Entered": "races_entered",
        "Races Started": "races_started",
        "Wins": "wins",
        "Points": "points",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Manufacturer", "Engines built in", "Seasons", "Wins"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }
