from scrapers.base.table.columns.types.column_factory import IntColumn
from scrapers.base.table.headers_shared import BASE_METRIC_HEADERS_TO_KEYS
from scrapers.base.table.patterns import SEPARATOR_PATTERN
from scrapers.base.table.patterns import TIME_12H_PATTERN
from scrapers.base.table.sentinels import SKIP_SENTINEL
from scrapers.seasons.columns.seasons import SeasonsColumn

HEADER_ROWS_WITH_SUBHEADERS = 2

skip = SKIP_SENTINEL

BASE_STATS_MAP = {
    "Seasons": "seasons",
    "Races Entered": "races_entered",
    "Races Started": "races_started",
    **BASE_METRIC_HEADERS_TO_KEYS,
    "WCC": "wcc",
    "WDC": "wdc",
}

BASE_STATS_COLUMNS = {
    "seasons": SeasonsColumn(),
    "races_entered": IntColumn(),
    "races_started": IntColumn(),
    "wins": IntColumn(),
    "points": IntColumn(),
    "poles": IntColumn(),
    "fastest_laps": IntColumn(),
    "podiums": IntColumn(),
    "wcc": IntColumn(),
    "wdc": IntColumn(),
}
