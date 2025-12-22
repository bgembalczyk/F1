_MONTHS = {
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

_LOCATION_STOPWORDS = {"and", "&"}

symbol_map = {
    "€": "EUR",
    "$": "USD",
    "£": "GBP",
    "¥": "JPY",
}

used_keys: set[str] = {
    "Location",
    "Coordinates",
    "FIA Grade",
    "Length",
    "Turns",
    "Race lap record",
    "Opened",
    "Closed",
    "Former names",
    "Owner",
    "Operator",
    "Capacity",
    "Broke ground",
    "Built",
    "Construction cost",
    "Website",
    "Area",
    "Major events",
    "Address",
    "Architect",
    "Banking",
    "Surface",
}

IGNORED_TOP_LEVEL_KEYS: set[str] = {
    "Owner",
    "owner",
    "Operator",
    "operator",
    "Capacity",
    "capacity",
    "Construction cost",
    "construction cost",
    "Website",
    "website",
    "Area",
    "area",
    "Major events",
    "major events",
    "Address",
    "address",
}
