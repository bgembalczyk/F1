from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleNamingAlias:
    old: str
    new: str


MODULE_NAMING_ALIASES: tuple[ModuleNamingAlias, ...] = (
    ModuleNamingAlias(
        old="scrapers.list_scraper_drivers",
        new="scrapers.drivers.list_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.list_scraper_seasons",
        new="scrapers.seasons.list_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.list_scraper_grands_prix",
        new="scrapers.grands_prix.list_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.constructors_list",
        new="scrapers.constructors_list_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.single_scraper_drivers",
        new="scrapers.drivers.single_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.constructors_single_scraper",
        new="scrapers.constructors.single_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.circuits_single_scraper",
        new="scrapers.circuits.single_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.single_scraper_seasons",
        new="scrapers.seasons.single_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.single_scraper_grands_prix",
        new="scrapers.grands_prix.single_scraper",
    ),
)


def module_naming_alias_map() -> dict[str, str]:
    return {entry.old: entry.new for entry in MODULE_NAMING_ALIASES}


from scrapers.legacy.module_naming_compat import MODULE_NAMING_ALIASES
from scrapers.legacy.module_naming_compat import ModuleNamingAlias
from scrapers.legacy.module_naming_compat import module_naming_alias_map

__all__ = ["MODULE_NAMING_ALIASES", "ModuleNamingAlias", "module_naming_alias_map"]
