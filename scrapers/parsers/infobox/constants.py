import re

MIN_RANGE_YEARS = 2
EXPECTED_STATS_COLUMNS = 3
TWO_DIGIT_YEAR_SUFFIX = 2
MIN_VALID_CAR_NUMBER_YEAR = 1900
MIN_YEAR_TOKENS_FOR_RANGE = 2
MIN_CAPACITY_VALUES_FOR_SEATING = 2
MIN_COORD_PARTS = 2
MIN_DETAILS_FOR_DRIVER = 1
MIN_DETAILS_FOR_CAR = 2
MIN_DETAILS_FOR_YEAR = 3
MIN_DETAILS_FOR_SERIES = 4

# Date pattern for matching common date formats
DATE_PATTERN = r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}|\b[A-Za-z]+\s+\d{1,2},\s*\d{4}|\b\d{4}\b"

# Regex patterns for year detection (compiled once for performance)
FOUR_DIGIT_YEAR_PATTERN = re.compile(r"^(19|20)\d{2}$")
TWO_DIGIT_SUFFIX_PATTERN = re.compile(r"^\d{2}$")
YEAR_TOKEN_RE = re.compile(r"\b\d{4}\b")
COUNT_RE = re.compile(r"^(\d+)")
PAREN_RE = re.compile(r"\(([^)]+)\)")
YEAR_FINDALL_RE = re.compile(r"\b\d{4}(?:[--]\d{4})?\b")
YEAR_RANGE_RE = re.compile(r"\b(\d{4})\s*[--]\s*(\d{2,4})\b")
YEAR_OPTIONAL_RANGE_RE = re.compile(r"\d{4}(?:[--]\d{4})?")
YEAR_OPTIONAL_RANGE_WS_RE = re.compile(r"\d{4}(?:\s*[--]\s*\d{2,4})?")
YEAR_RANGE_STRICT_RE = re.compile(r"\d{4}\s*[--]\s*\d{2,4}")
HAS_YEARS_RE = re.compile(r"\(\s*\d{4}")
BR_SPLIT_RE = re.compile(r"<br\s*/?>", flags=re.IGNORECASE)
YEAR_PAREN_RE = re.compile(r"\s*\([^)]*\d{4}[^)]*\)")
YEAR_PATTERNS_RE = re.compile(r"\(([^)]*\d{4}[^)]*)\)")
YEAR_RANGE_RE_NAT = re.compile(r"(\d{4})\s*[--]\s*(\d{4})")
YEAR_RE = re.compile(r"\b(\d{4})\b")
JUST_REF_MARKER_RE = re.compile(r"^\[\d+\]$")
OR_SPLIT_RE = re.compile(r"\s+or\s+", flags=re.IGNORECASE)
REF_MARKER_RE = re.compile(r"\[\d+\]")
OPEN_ENDED_RE = re.compile(r"\b(\d{4})\s*[-\u2013]\s*(?:present)?$")
# tylko markery językowe w nawiasie: (es), ( de ), (it)
LANG_PAREN_ANYWHERE_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)", flags=re.IGNORECASE)

# do czyszczenia uciętych markerów typu "( es" / "( cs"
LANG_PAREN_TAIL_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)?\s*$", flags=re.IGNORECASE)

ENTITY_PARTS_RE = re.compile(r"\s*(?:,|&|\band\b)\s*", flags=re.IGNORECASE)

CAR_NUMBER_PATTERN_RE = re.compile(
    r"(?<!\d)(?P<prefix>No\.?|#|№)?\s*(?P<number>\d+)\s*(?:\((?P<years>[^)]+)\))?",
    re.IGNORECASE,
)

ACTIVE_YEARS_LABELS = {"Active years", "Years active", "Years"}
TEAM_LABELS = {"Teams", "Former teams"}
LOCATION_STOPWORDS = {"and", "&"}

INT_CELL_LABELS = {
    "Wins",
    "Podiums",
    "Pole positions",
    "Poles",
    "Fastest laps",
    "Starts",
}
RACE_EVENT_LABELS = {
    "First race",
    "Last race",
    "First win",
    "Last win",
    "First entry",
    "Last entry",
}
used_keys: set[str] = {
    "location",
    "coordinates",
    "fia_grade",
    "length",
    "turns",
    "race_lap_record",
    "opened",
    "closed",
    "former_names",
    "owner",
    "operator",
    "capacity",
    "broke_ground",
    "built",
    "construction_cost",
    "website",
    "area",
    "major_events",
    "address",
    "architect",
    "banking",
    "surface",
}

IGNORED_TOP_LEVEL_KEYS: set[str] = {
    "owner",
    "operator",
    "capacity",
    "construction_cost",
    "website",
    "area",
    "major_events",
    "address",
}


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

symbol_map = {
    "€": "EUR",
    "$": "USD",
    "£": "GBP",
    "¥": "JPY",
}
MATERIAL_PATTERNS = {
    "Asphalt": ("tarmac", "asphalt", "asphalt concrete"),
    "Concrete": ("concrete",),
    "Cobblestones": ("cobblestone", "cobbles", "cobbl"),
    "Brick": ("brick",),
    "Wood": ("wood",),
    "Dirt": ("dirt",),
    "Steel": ("steel",),
    "Graywacke": ("graywacke",),
}
