from typing import Any

from scrapers.constructors_constants import CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_BASED_IN_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_ENGINE_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_FASTEST_LAPS_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_NAME_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_POLES_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_RACES_ENTERED_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_RACES_STARTED_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_TOTAL_ENTRIES_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_WCC_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_WDC_HEADER
from scrapers.constructors_constants import CONSTRUCTOR_WINS_HEADER
from scrapers.wiki.parsers.elements.wiki_table import WikiTableBaseParser


class CurrentConstructorsTableParser(WikiTableBaseParser):
    table_type = "current_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        expected = {
            CONSTRUCTOR_NAME_HEADER.lower(),
            CONSTRUCTOR_ENGINE_HEADER.lower(),
            CONSTRUCTOR_LICENSED_IN_HEADER.lower(),
            CONSTRUCTOR_BASED_IN_HEADER.lower(),
            CONSTRUCTOR_SEASONS_HEADER.lower(),
            CONSTRUCTOR_RACES_ENTERED_HEADER.lower(),
            CONSTRUCTOR_RACES_STARTED_HEADER.lower(),
            CONSTRUCTOR_TOTAL_ENTRIES_HEADER.lower(),
            CONSTRUCTOR_WINS_HEADER.lower(),
            CONSTRUCTOR_POINTS_HEADER.lower(),
            CONSTRUCTOR_POLES_HEADER.lower(),
            CONSTRUCTOR_FASTEST_LAPS_HEADER.lower(),
            CONSTRUCTOR_PODIUMS_HEADER.lower(),
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
        CONSTRUCTOR_SEASONS_HEADER: "seasons",
        CONSTRUCTOR_RACES_ENTERED_HEADER: "races_entered",
        CONSTRUCTOR_RACES_STARTED_HEADER: "races_started",
        CONSTRUCTOR_DRIVERS_HEADER: "drivers",
        CONSTRUCTOR_TOTAL_ENTRIES_HEADER: "total_entries",
        CONSTRUCTOR_WINS_HEADER: "wins",
        CONSTRUCTOR_POINTS_HEADER: "points",
        CONSTRUCTOR_POLES_HEADER: "poles",
        CONSTRUCTOR_FASTEST_LAPS_HEADER: "fastest_laps",
        CONSTRUCTOR_PODIUMS_HEADER: "podiums",
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
