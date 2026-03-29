import re

MIN_CAPACITY_VALUES_FOR_SEATING = 2
MIN_COORD_PARTS = 2
MIN_DETAILS_FOR_DRIVER = 1
MIN_DETAILS_FOR_CAR = 2
MIN_DETAILS_FOR_YEAR = 3
MIN_DETAILS_FOR_SERIES = 4


# tylko markery językowe w nawiasie: (es), ( de ), (it)
LANG_PAREN_ANYWHERE_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)", flags=re.IGNORECASE)

# do czyszczenia uciętych markerów typu "( es" / "( cs"
LANG_PAREN_TAIL_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)?\s*$", flags=re.IGNORECASE)

ENTITY_PARTS_RE = re.compile(r"\s*(?:,|&|\band\b)\s*", flags=re.IGNORECASE)


LOCATION_STOPWORDS = {"and", "&"}


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
