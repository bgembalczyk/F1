from typing import Any

from scrapers.constants.constructors_constants import (
    CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER,
)
from scrapers.constants.constructors_constants import CONSTRUCTOR_BASED_IN_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_ENGINE_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_FASTEST_LAPS_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_NAME_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_POLES_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_RACES_ENTERED_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_RACES_STARTED_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_TOTAL_ENTRIES_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_WCC_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_WDC_HEADER
from scrapers.constants.constructors_constants import CONSTRUCTOR_WINS_HEADER
from scrapers.constants.shared_headers import SHARED_PODIUMS_HEADER
from scrapers.constants.shared_headers import SHARED_POINTS_HEADER
from scrapers.constants.shared_headers import SHARED_SEASONS_HEADER
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper


class CurrentConstructorsTableMapper(WikiTableBaseMapper):
    table_type = "current_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        expected = {
            CONSTRUCTOR_NAME_HEADER.lower(),
            CONSTRUCTOR_ENGINE_HEADER.lower(),
            CONSTRUCTOR_LICENSED_IN_HEADER.lower(),
            CONSTRUCTOR_BASED_IN_HEADER.lower(),
            SHARED_SEASONS_HEADER.lower(),
            CONSTRUCTOR_RACES_ENTERED_HEADER.lower(),
            CONSTRUCTOR_RACES_STARTED_HEADER.lower(),
            CONSTRUCTOR_TOTAL_ENTRIES_HEADER.lower(),
            CONSTRUCTOR_WINS_HEADER.lower(),
            SHARED_POINTS_HEADER.lower(),
            CONSTRUCTOR_POLES_HEADER.lower(),
            CONSTRUCTOR_FASTEST_LAPS_HEADER.lower(),
            SHARED_PODIUMS_HEADER.lower(),
            CONSTRUCTOR_WCC_HEADER.lower(),
            CONSTRUCTOR_WDC_HEADER.lower(),
            CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER.lower(),
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    _HEADER_TO_KEY: dict[str, str] = {
        CONSTRUCTOR_NAME_HEADER: "constructor",
        CONSTRUCTOR_ENGINE_HEADER: "engine",
        CONSTRUCTOR_LICENSED_IN_HEADER: "licensed_in",
        CONSTRUCTOR_BASED_IN_HEADER: "based_in",
        SHARED_SEASONS_HEADER: "seasons",
        CONSTRUCTOR_RACES_ENTERED_HEADER: "races_entered",
        CONSTRUCTOR_RACES_STARTED_HEADER: "races_started",
        CONSTRUCTOR_DRIVERS_HEADER: "drivers",
        CONSTRUCTOR_TOTAL_ENTRIES_HEADER: "total_entries",
        CONSTRUCTOR_WINS_HEADER: "wins",
        SHARED_POINTS_HEADER: "points",
        CONSTRUCTOR_POLES_HEADER: "poles",
        CONSTRUCTOR_FASTEST_LAPS_HEADER: "fastest_laps",
        SHARED_PODIUMS_HEADER: "podiums",
        CONSTRUCTOR_WCC_HEADER: "wcc_titles",
        CONSTRUCTOR_WDC_HEADER: "wdc_titles",
        CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER: "antecedent_teams",
    }

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._HEADER_TO_KEY.get(
                header.strip(),
                header.strip().lower().replace(" ", "_"),
            )
            for header in headers
        }

    def parse_row(
        self,
        row: dict[str, Any],
        column_map: dict[str, str],
    ) -> dict[str, Any]:
        mapped = super().parse_row(row, column_map)
        normalized = dict(mapped)
        if "constructor" in normalized:
            chassis = self._normalize_constructor_link(normalized.get("constructor"))
            engine = (
                self._normalize_constructor_link(normalized.get("engine")) or chassis
            )
            normalized["constructor"] = {
                "chassis_constructor": chassis,
                "engine_constructor": engine,
            }
            normalized.pop("engine", None)
        return self._sort_record_keys(normalized)

    @staticmethod
    def _normalize_constructor_link(value: Any) -> dict[str, Any] | None:
        if isinstance(value, list):
            if not value:
                return None
            value = value[0]
        if isinstance(value, dict):
            text = value.get("text")
            url = value.get("url")
            normalized: dict[str, Any] = {}
            if text is not None:
                normalized["text"] = text
            if url is not None:
                normalized["url"] = url
            return normalized or None
        if isinstance(value, str):
            return {"text": value}
        return None

    @staticmethod
    def _sort_record_keys(record: dict[str, Any]) -> dict[str, Any]:
        ordered: dict[str, Any] = {}
        if "constructor" in record:
            ordered["constructor"] = record["constructor"]
        for key in sorted(key for key in record if key != "constructor"):
            ordered[key] = record[key]
        return ordered
