import re

CLASSIFIED_DNF_MARK = "†"
CLASSIFIED_DNF_NOTE = "classified_after_dnf_90_percent"
CLASSIFIED_DNF_START_YEAR = 1985

SHARED_DRIVE_NO_POINTS_START_YEAR = 1960
SHARED_DRIVE_NO_POINTS_END_YEAR = 1964
SHARED_DRIVE_POINTS_START_YEAR = 1950
SHARED_DRIVE_POINTS_END_YEAR = 1957

FATAL_NOTES_START_YEAR = 1965
DOUBLE_POINTS_SEASON_YEAR = 2014
SPRINT_POINTS_START_YEAR = 2021
LAST_YEAR_FORMULA_ONE_SEASON = 1980

SHORT_HEX_COLOR_LENGTH = 3

CC_TO_L_THRESHOLD = 100
ENGINE_CONSTRUCTOR_INDEX = 1

NORMALIZE_COMMA_AND_RE = re.compile(r",\s*and\s+", flags=re.IGNORECASE)
NORMALIZE_SPACE_AND_RE = re.compile(r"\s+and\s+", flags=re.IGNORECASE)
NORMALIZE_START_AND_RE = re.compile(r"^\s*and\s+", flags=re.IGNORECASE)

YEAR_PATTERN = re.compile(r"^\d{4}$")
YEAR_IN_URL_PATTERN = re.compile(r"(?<!\d)\d{4}(?!\d)")

# Pattern for range separators
SEPARATOR_PATTERN = re.compile(r"\s*[-—]\s*")
FOOTNOTE_RE = re.compile(r"\d+")
LETTER_RE = re.compile(r"[A-Za-z]")
# Pattern that matches a displacement value followed by an explicit unit (e.g. "1.5 L",
# "1.5 L8" where L starts the type, "3000cc") or a bare decimal (e.g. "3.0 V8").
DISPLACEMENT_RE = re.compile(
    r"\b\d+\.?\d*\s*(?:L|l|litre|litres|cc|cm³)|\b\d+\.\d+\b",
)

# Exact engine type code (e.g. "V8", "L4", "F4").
EXACT_TYPE_RE = re.compile(r"^[A-Za-z]\d+$")

# Engine type code with a single-character modifier suffix:
#   't' suffix → turbocharged  (e.g. "L4t")
#   's' suffix → supercharged  (e.g. "L4s")
TYPE_WITH_MODIFIER_RE = re.compile(r"^([A-Za-z]\d+)([ts])$", re.IGNORECASE)

# Engine type embedded at end of text after a displacement number
# (e.g. "Climax FPF 2.0 L4" → "L4", "620 3.0 V8" → "V8").
AFTER_DISPLACEMENT_TYPE_RE = re.compile(r"\b\d+\.?\d*\s+([A-Za-z]\d+)\s*$")

# Engine type code appearing anywhere in plain text
# (e.g. "V12", "V8", "L4" after displacement).
# Restricted to known layout letters and 1-2 digit cylinder counts
# to avoid false positives.
PLAIN_TEXT_TYPE_RE = re.compile(r"\b([VLFHR]\d{1,2}[ts]?)\b")

# Compiled pattern for detecting a 3-digit CSS hex colour (after lower-casing).
CSS_3DIGIT_HEX_RE = re.compile(r"^#[0-9a-f]{3}$")
RE_COLON = re.compile(r"^\s*(?P<min>\d+)\s*:\s*(?P<sec>\d+(?:\.\d+)?)\s*$")
POINTS_WITH_TOTAL_RE = re.compile(r"^(.*?)\(([^)]+)\)")
MARKS_RE = re.compile(r"[†‡✝✚*~^]")
SPLIT_RESULTS_RE = re.compile(r"\s*/\s*")

RE_MINSEC = re.compile(
    r"^\s*(?:(?P<min>\d+)\s*(?:m|min|minutes?)\s*)?"
    r"(?P<sec>\d+(?:\.\d+)?)\s*(?:s|sec|seconds?)\s*$",
    re.IGNORECASE,
)
RE_SECONDS = re.compile(
    r"^\s*(?P<sec>\d+(?:\.\d+)?)\s*(?:s|sec|seconds?)?\s*$",
    re.IGNORECASE,
)
FRACTION_RE = re.compile(
    r"(?:(?P<whole>\d+)\s+)?(?P<numerator>\d+)\s*[/\u2044]\s*(?P<denominator>\d+)",
)


F2_INELIGIBLE_YEARS = {1957, 1958, 1966, 1967, 1969}

# F1 and F2 designate Formula racing classes, not Flat-1 / Flat-2 engine layouts.
FORMULA_CLASS_TYPE_CODES: frozenset[str] = frozenset({"F1", "F2"})

# Dash variants that separate chassis from engine constructor in a cell.
HYPHEN_CHARS: frozenset[str] = frozenset({"-", "\u2013", "\u2014", "\u2212"})


CLASSIFIED_DNF_BACKGROUNDS = {
    "Winner",
    "Second place",
    "Third place",
    "Other points position",
    "Other classified position",
}

BACKGROUND_TO_RESULT = {
    "ffffbf": "Winner",
    "dfdfdf": "Second place",
    "ffdf9f": "Third place",
    "dfffdf": "Other points position",
    "cfcfff": "Other classified position",
    "efcfff": "Not classified, retired",
    "ffcfcf": "Did not qualify",
    "000000": "Disqualified",
    "ffffff": "Did not start",
}

# Mapping from verbose/human-readable engine type names
# (as they appear in Wikipedia link text)
# to canonical type codes.
VERBOSE_TYPE_MAP: dict[str, str] = {
    "straight-4": "L4",
    "inline-four": "L4",
    "inline-four engine": "L4",
    "straight-4 engine": "L4",
    "flat-4": "F4",
    "horizontally opposed 4": "F4",
    "straight-6": "L6",
    "inline-six": "L6",
    "inline-six engine": "L6",
    "straight-6 engine": "L6",
    "flat-6": "F6",
    "straight-8": "L8",
    "inline-eight": "L8",
    "straight-8 engine": "L8",
    "flat-8": "F8",
    "v6": "V6",
    "v6 engine": "V6",
    "v8": "V8",
    "v8 engine": "V8",
    "v10": "V10",
    "v10 engine": "V10",
    "v12": "V12",
    "v12 engine": "V12",
    "v16": "V16",
    "flat-12": "F12",
    "flat-16": "F16",
    "h16": "H16",
}

# URL fragments that indicate a fuel-type modifier (not a standalone engine model).
FUEL_TYPE_URLS: dict[str, str] = {
    "diesel_engine": "diesel",
    "diesel fuel": "diesel",
}

# URL fragments that indicate the link describes only a modifier
# (fuel type or induction), not an engine model.
# When a segment contains only such a link it should be treated as
# a modifier to the preceding engine rather than a new engine entry.
MODIFIER_ONLY_URLS: frozenset[str] = frozenset(
    {
        "diesel_engine",
        "supercharger",
        "supercharged",
        "turbocharger",
        "turbocharging",
        "gas_turbine",
    },
)

TYRE_NAME_BY_CODE = {
    "A": "Avon",
    "B": "Bridgestone",
    "C": "Continental",
    "D": "Dunlop",
    "E": "Englebert",
    "F": "Firestone",
    "G": "Goodyear",
    "M": "Michelin",
    "P": "Pirelli",
}
