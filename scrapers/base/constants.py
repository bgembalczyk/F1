import re

from scrapers.base.run_profiles import RunProfileName


CliMainProfile = RunProfileName


HEADER_SUFFIX = "_HEADER"
SECTION_ID_SUFFIX = "_SECTION_ID"
URL_SUFFIX = "_URL"

LOGGER_NAME = "f1.scrapers"


UNIT_RE = re.compile(
    r"(?P<value>[-+]?\d[\d,]*(?:\.\d+)?)\s*"
    r"(?P<unit>cm³|cm3|cc|l|litre|litres|bar)\b",
    flags=re.IGNORECASE,
)
ANGLE_RE = re.compile(
    r"(?P<value>[-+]?\d[\d,]*(?:\.\d+)?)\s*(?:°|deg|degrees?)",
    flags=re.IGNORECASE,
)
CONFIG_TYPE_RE = re.compile(r"\b([A-Z]{1,2}\d+)\b")
MAX_CYLINDERS_RE = re.compile(r"\bup to\s+(?P<value>\d+)\s+cylinders?\b", re.IGNORECASE)
RANGE_RE = re.compile(
    r"(?P<min>[-+]?\d[\d,]*(?:\.\d+)?)\s*-\s*(?P<max>[-+]?\d[\d,]*(?:\.\d+)?)",
    flags=re.IGNORECASE,
)


PROFILE_DEFAULTS: dict[CliMainProfile, tuple[bool, bool]] = {
    RunProfileName.STRICT: (True, False),
    RunProfileName.MINIMAL: (False, False),
    RunProfileName.DEPRECATED: (True, False),
}


LEGACY_PROFILE_ALIASES: dict[str, RunProfileName] = {
    "list_scraper": RunProfileName.STRICT,
    "complete_extractor": RunProfileName.MINIMAL,
    "deprecated_entrypoint": RunProfileName.DEPRECATED,
}


NAMING_CONVENTIONS = {
    "header": {
        "suffix": HEADER_SUFFIX,
        "example": "DRIVER_NAME_HEADER",
    },
    "section_id": {
        "suffix": SECTION_ID_SUFFIX,
        "example": "DRIVERS_SECTION_ID",
    },
    "url": {
        "suffix": URL_SUFFIX,
        "example": "DRIVERS_LIST_URL",
    },
}

SCRAPER_CONSTANT_PREFIXES = {
    "scrapers.circuits.constants": ("CIRCUIT",),
    "scrapers.constructors.constants": ("CONSTRUCTOR", "CONSTRUCTORS"),
    "scrapers.drivers.constants": (
        "DRIVER",
        "DRIVERS",
        "FATALITIES",
        "FEMALE_DRIVER",
        "FEMALE_DRIVERS",
    ),
    "scrapers.points.constants": ("POINTS",),
}
