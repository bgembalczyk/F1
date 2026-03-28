HEADER_SUFFIX = "_HEADER"
SECTION_ID_SUFFIX = "_SECTION_ID"
URL_SUFFIX = "_URL"


NAMING_CONVENTIONS = {
    "header": {
        "suffix": HEADER_SUFFIX,
        "group": "contextual_headers",
        "pattern": "<CONTEXT>_<FIELD>_HEADER",
        "example": "DRIVER_NAME_HEADER",
    },
    "section_id": {
        "suffix": SECTION_ID_SUFFIX,
        "group": "wiki_sections",
        "pattern": "<CONTEXT>_<TARGET>_SECTION_ID",
        "example": "FATALITIES_SECTION_ID",
    },
    "url": {
        "suffix": URL_SUFFIX,
        "group": "source_endpoints",
        "pattern": "<CONTEXT>_<TARGET>_URL",
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
