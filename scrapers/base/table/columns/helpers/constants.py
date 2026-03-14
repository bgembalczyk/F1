import re

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

# Compiled pattern for detecting a 3-digit CSS hex colour (after lower-casing).
CSS_3DIGIT_HEX_RE = re.compile(r"^#[0-9a-f]{3}$")
CC_TO_L_THRESHOLD = 100
