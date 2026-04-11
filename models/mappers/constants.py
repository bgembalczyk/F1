FIELD_ALIASES: dict[str, dict[str, str]] = {
    "constructor": {
        "wcc": "wcc_titles",
        "wdc": "wdc_titles",
    },
    "driver": {
        "entries": "race_entries",
        "starts": "race_starts",
        "poles": "pole_positions",
    },
    "grands_prix": {
        "title": "race_title",
        "status": "race_status",
        "years": "years_held",
        "seasons": "years_held",
    },
}
