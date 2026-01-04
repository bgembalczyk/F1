HEADER_SUFFIX = "_HEADER"
SECTION_ID_SUFFIX = "_SECTION_ID"
URL_SUFFIX = "_URL"

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
