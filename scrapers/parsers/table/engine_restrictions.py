from typing import Any

from scrapers.parsers.table.wiki.base import WikiTableBaseParser


class EngineRestrictionsTableParser(WikiTableBaseParser):
    table_type = "engine_restrictions"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Year": "year",
        "2000-2005": "rules_2000_2005",
        "2006-2013": "rules_2006_2013",
        "2014-2025": "rules_2014_2025",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Year", "2000-2005", "2006-2013", "2014-2025"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }
