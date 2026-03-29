import re

from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types.column_factory import IntColumn
from scrapers.base.table.headers_shared import BASE_METRIC_HEADERS_TO_KEYS
from scrapers.base.table.sentinels import SKIP_SENTINEL

HEADER_ROWS_WITH_SUBHEADERS = 2

skip = SKIP_SENTINEL

# Pattern for time in 12-hour format with am/pm
TIME_12H_PATTERN = re.compile(r"(\d{1,2}):(\d{2})\s*(am|pm)", re.IGNORECASE)

# Pattern for range separators
SEPARATOR_PATTERN = re.compile(r"\s*[-—]\s*")

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
