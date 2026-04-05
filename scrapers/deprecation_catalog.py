from __future__ import annotations

from dataclasses import dataclass

DEPRECATED_SINCE = "2026-01-01"
REMOVE_AFTER = "2026-12-31"


@dataclass(frozen=True)
class DeprecatedModuleEntry:
    module_path: str
    replacement_module_path: str | None = None


DEPRECATED_MODULES: tuple[DeprecatedModuleEntry, ...] = (
    DeprecatedModuleEntry(
        "scrapers.circuits.list_scraper",
        "scrapers.circuits.entrypoint",
    ),
    DeprecatedModuleEntry("scrapers.circuits.complete_scraper"),
    DeprecatedModuleEntry(
        "scrapers.constructors.current_constructors_list",
        "scrapers.constructors.entrypoint",
    ),
    DeprecatedModuleEntry("scrapers.constructors.former_constructors_list"),
    DeprecatedModuleEntry("scrapers.constructors.indianapolis_only_constructors_list"),
    DeprecatedModuleEntry("scrapers.constructors.privateer_teams_list"),
    DeprecatedModuleEntry("scrapers.constructors.complete_scraper"),
    DeprecatedModuleEntry(
        "scrapers.drivers.list_scraper",
        "scrapers.drivers.entrypoint",
    ),
    DeprecatedModuleEntry("scrapers.drivers.female_drivers_list"),
    DeprecatedModuleEntry("scrapers.drivers.fatalities_list_scraper"),
    DeprecatedModuleEntry("scrapers.drivers.complete_scraper"),
    DeprecatedModuleEntry("scrapers.engines.engine_manufacturers_list"),
    DeprecatedModuleEntry(
        "scrapers.engines.indianapolis_only_engine_manufacturers_list",
    ),
    DeprecatedModuleEntry("scrapers.engines.engine_regulation"),
    DeprecatedModuleEntry("scrapers.engines.engine_restrictions"),
    DeprecatedModuleEntry("scrapers.engines.complete_scraper"),
    DeprecatedModuleEntry(
        "scrapers.grands_prix.list_scraper",
        "scrapers.grands_prix.entrypoint",
    ),
    DeprecatedModuleEntry("scrapers.grands_prix.complete_scraper"),
    DeprecatedModuleEntry(
        "scrapers.races.red_flagged_races_scraper.world_championship",
    ),
    DeprecatedModuleEntry("scrapers.points.points_scoring_systems_history"),
    DeprecatedModuleEntry("scrapers.points.shortened_race_points"),
    DeprecatedModuleEntry("scrapers.points.sprint_qualifying_points"),
    DeprecatedModuleEntry(
        "scrapers.seasons.list_scraper",
        "scrapers.seasons.entrypoint",
    ),
    DeprecatedModuleEntry("scrapers.seasons.complete_scraper"),
    DeprecatedModuleEntry("scrapers.sponsorship_liveries.scraper"),
    DeprecatedModuleEntry("scrapers.tyres.list_scraper"),
)


def get_deprecated_module_migrations() -> list[tuple[str, str]]:
    return sorted(
        (
            item.module_path,
            item.replacement_module_path or item.module_path,
        )
        for item in DEPRECATED_MODULES
    )


def get_deprecated_elements_report() -> list[tuple[str, str, str, str]]:
    return [
        (
            item.module_path,
            DEPRECATED_SINCE,
            item.replacement_module_path or item.module_path,
            REMOVE_AFTER,
        )
        for item in sorted(DEPRECATED_MODULES, key=lambda x: x.module_path)
    ]
