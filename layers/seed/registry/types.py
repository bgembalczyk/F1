from __future__ import annotations

from enum import Enum


class SeedName(str, Enum):
    CIRCUITS = "circuits"
    CONSTRUCTORS = "constructors"
    CONSTRUCTORS_CURRENT = "constructors_current"
    CONSTRUCTORS_FORMER = "constructors_former"
    CONSTRUCTORS_INDIANAPOLIS_ONLY = "constructors_indianapolis_only"
    CONSTRUCTORS_PRIVATEER = "constructors_privateer"
    DRIVERS = "drivers"
    DRIVERS_FEMALE = "drivers_female"
    DRIVERS_FATALITIES = "drivers_fatalities"
    SEASONS = "seasons"
    GRANDS_PRIX = "grands_prix"
    GRANDS_PRIX_BY_TITLE = "grands_prix_by_title"
    ENGINES_INDIANAPOLIS_ONLY = "engines_indianapolis_only"
    ENGINES_RESTRICTIONS = "engines_restrictions"
    ENGINES_REGULATIONS = "engines_regulations"
    ENGINES_MANUFACTURERS = "engines_manufacturers"
    GRANDS_PRIX_RED_FLAGGED_WORLD_CHAMPIONSHIP = (
        "grands_prix_red_flagged_world_championship"
    )
    GRANDS_PRIX_RED_FLAGGED_NON_CHAMPIONSHIP = (
        "grands_prix_red_flagged_non_championship"
    )
    POINTS_SPRINT = "points_sprint"
    POINTS_SHORTENED = "points_shortened"
    POINTS_HISTORY = "points_history"
    TYRES = "tyres"
    SPONSORSHIP_LIVERIES = "sponsorship_liveries"


class DomainName(str, Enum):
    CIRCUITS = "circuits"
    CONSTRUCTORS = "constructors"
    CHASSIS_CONSTRUCTORS = "chassis_constructors"
    DRIVERS = "drivers"
    SEASONS = "seasons"
    GRANDS_PRIX = "grands_prix"
    ENGINES = "engines"
    RULES = "rules"
    RACES = "races"
    POINTS = "points"
    TEAMS = "teams"


class RunProfile(str, Enum):
    STRICT = "strict"
    MINIMAL = "minimal"
    DEBUG = "debug"
    DEPRECATED = "deprecated"


def parse_seed_name(value: str) -> SeedName:
    try:
        return SeedName(value)
    except ValueError as exc:
        supported = ", ".join(seed.value for seed in SeedName)
        msg = f"Unsupported seed_name '{value}'. Supported values: {supported}."
        raise ValueError(msg) from exc


def parse_domain_name(value: str) -> DomainName:
    try:
        return DomainName(value)
    except ValueError as exc:
        supported = ", ".join(domain.value for domain in DomainName)
        msg = f"Unsupported domain '{value}'. Supported values: {supported}."
        raise ValueError(msg) from exc


def parse_run_profile(value: str) -> RunProfile:
    try:
        return RunProfile(value)
    except ValueError as exc:
        supported = ", ".join(profile.value for profile in RunProfile)
        msg = f"Unsupported run profile '{value}'. Supported values: {supported}."
        raise ValueError(msg) from exc
