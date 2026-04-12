from typing import Any

from scrapers.parsers.wiki_table_base_mapper import WikiTableBaseMapper


class SeasonsTableMapper(WikiTableBaseMapper):
    table_type = "seasons_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Season": "season",
        "Races": "races",
        "Countries": "countries",
        "First": "first",
        "Last": "last",
        "Drivers' Champion (team)": "drivers_champion_team",
        "Constructors' Champion": "constructors_champion",
        "Winners": "winners",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Season", "Races"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }
