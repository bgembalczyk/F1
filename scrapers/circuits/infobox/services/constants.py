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

LOCATION_STOPWORDS = {"and", "&"}

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

MIN_CAPACITY_VALUES_FOR_SEATING = 2

MIN_COORD_PARTS = 2
