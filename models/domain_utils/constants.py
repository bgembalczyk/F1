import re

SHORT_YEAR_DIGITS = 2
YEAR_PATTERN = re.compile(r"^\d{4}$")
YEAR_RANGE_PATTERN = re.compile(
    r"^(\d{4})\s*[\-\u2013\u2014]\s*(\d{2,4}|present)$",
    re.IGNORECASE,
)
YEAR_TO_PATTERN = re.compile(r"^(\d{4})\s+to\s+(\d{2,4}|present)$", re.IGNORECASE)
ONWARDS_PATTERN = re.compile(r"(\d{4})\s+onward(?:s)?\b", re.IGNORECASE)
PRESENT_PATTERN = re.compile(r"\bpresent\b", re.IGNORECASE)


NUMERIC_DASH_RANGE_PATTERN = re.compile(r"^(\d+)\s*[\-\u2013\u2014]\s*(\d+)$")

EXPLICIT_RANGE_PATTERNS = (
    re.compile(r"\b(\d{4})\s*[\-\u2013\u2014]\s*(\d{2,4}|present)\b", re.IGNORECASE),
    re.compile(r"\b(\d{4})\s+to\s+(\d{2,4}|present)\b", re.IGNORECASE),
)
