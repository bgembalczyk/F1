import re

MIN_RANGE_YEARS = 2
EXPECTED_STATS_COLUMNS = 3
TWO_DIGIT_YEAR_SUFFIX = 2
MIN_VALID_CAR_NUMBER_YEAR = 1900
MIN_YEAR_TOKENS_FOR_RANGE = 2

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

CAR_NUMBER_PATTERN_RE = re.compile(
    r"(?<!\d)(?P<prefix>No\.?|#|№)?\s*(?P<number>\d+)\s*(?:\((?P<years>[^)]+)\))?",
    re.IGNORECASE,
)

ACTIVE_YEARS_LABELS = {"Active years", "Years active", "Years"}
TEAM_LABELS = {"Teams", "Former teams"}
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


__all__ = [
    "MIN_RANGE_YEARS",
    "EXPECTED_STATS_COLUMNS",
    "TWO_DIGIT_YEAR_SUFFIX",
    "MIN_VALID_CAR_NUMBER_YEAR",
    "MIN_YEAR_TOKENS_FOR_RANGE",
    "DATE_PATTERN",
    "FOUR_DIGIT_YEAR_PATTERN",
    "TWO_DIGIT_SUFFIX_PATTERN",
    "YEAR_TOKEN_RE",
    "COUNT_RE",
    "PAREN_RE",
    "YEAR_FINDALL_RE",
    "YEAR_RANGE_RE",
    "YEAR_OPTIONAL_RANGE_RE",
    "YEAR_OPTIONAL_RANGE_WS_RE",
    "YEAR_RANGE_STRICT_RE",
    "HAS_YEARS_RE",
    "BR_SPLIT_RE",
    "YEAR_PAREN_RE",
    "YEAR_PATTERNS_RE",
    "YEAR_RANGE_RE_NAT",
    "YEAR_RE",
    "JUST_REF_MARKER_RE",
    "OR_SPLIT_RE",
    "REF_MARKER_RE",
    "OPEN_ENDED_RE",
    "CAR_NUMBER_PATTERN_RE",
    "ACTIVE_YEARS_LABELS",
    "TEAM_LABELS",
    "INT_CELL_LABELS",
    "RACE_EVENT_LABELS",
]
