SEED_RECORD_SCHEMA_VERSION = "1.0"

COMPONENT_METADATA_ATTR = "COMPONENT_METADATA"

FORMER_CONSTRUCTORS_SOURCE = "f1_former_constructors.json"
INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE = "f1_indianapolis_only_constructors.json"
TYRE_MANUFACTURERS_SOURCE = "f1_tyre_manufacturers_by_season.json"
F1_DRIVERS_SOURCE = "f1_drivers.json"
FEMALE_DRIVERS_SOURCE = "female_drivers.json"
DRIVER_FATALITIES_SOURCE = "f1_driver_fatalities.json"
SPONSORSHIP_LIVERIES_SOURCE = "f1_sponsorship_liveries.json"
PRIVATEER_TEAMS_SOURCE = "f1_privateer_teams.json"
F1_RED_FLAGGED_WORLD_CHAMPIONSHIP_SOURCE = (
    "f1_red_flagged_world_championship_races.json"
)
F1_RED_FLAGGED_NON_CHAMPIONSHIP_SOURCE = (
    "f1_red_flagged_non_championship_races.json"
)
F1_ENGINE_MANUFACTURERS_SOURCE = "f1_engine_manufacturers.json"
F1_INDIANAPOLIS_ONLY_ENGINE_MANUFACTURERS_SOURCE = (
    "f1_indianapolis_only_engine_manufacturers.json"
)
F1_CONSTRUCTORS_BY_YEAR_PATTERN = r"f1_constructors_\d{4}\.json"

FORMULA_ONE_SERIES = ["Formula One"]
CHASSIS_CONSTRUCTOR_DOMAINS = {"constructors", "chassis_constructors"}

NAME_CANDIDATE_KEYS = (
    "name",
    "driver",
    "constructor",
    "team",
    "circuit",
    "race_title",
    "season",
    "manufacturer",
)
LINK_CANDIDATE_KEYS = (
    "link",
    "url",
    "driver_url",
    "constructor_url",
    "team_url",
    "circuit_url",
)
CIRCUITS_FORMULA_ONE_FIELDS = {
    "circuit_status",
    "last_length_used_km",
    "last_length_used_mi",
    "turns",
    "grands_prix",
    "seasons",
    "grands_prix_held",
}
CONSTRUCTORS_FORMULA_ONE_FIELDS = {
    "engine",
    "licensed_in",
    "based_in",
    "seasons",
    "races_entered",
    "races_started",
    "drivers",
    "total_entries",
    "wins",
    "points",
    "poles",
    "fastest_laps",
    "podiums",
    "wcc_titles",
    "wdc_titles",
    "antecedent_teams",
    "status",
}
ENGINES_FORMULA_ONE_FIELDS = {
    "manufacturer_status",
    "engines_built_in",
    "seasons",
    "races_entered",
    "races_started",
    "wins",
    "points",
    "poles",
    "fastest_laps",
    "podiums",
    "wcc",
    "wdc",
}
GRANDS_PRIX_FORMULA_ONE_FIELDS = {
    "race_status",
    "country",
    "years_held",
    "circuits",
    "total",
}

RED_FLAG_FIELDS = (
    "lap",
    "restart_status",
    "winner",
    "incident",
    "failed_to_make_restart",
)
