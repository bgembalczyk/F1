"""Temporary import aliases for module naming migration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleNamingAlias:
    old: str
    new: str


MODULE_NAMING_ALIASES: tuple[ModuleNamingAlias, ...] = (
    ModuleNamingAlias(
        old="scrapers.list_scraper_drivers",
        new="scrapers.drivers_list_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.list_scraper_seasons",
        new="scrapers.seasons_list_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.list_scraper_grands_prix",
        new="scrapers.grands_prix_list_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.single_scraper_drivers",
        new="scrapers.drivers_detail_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.constructors_single_scraper",
        new="scrapers.constructors_detail_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.circuits_single_scraper",
        new="scrapers.circuits_detail_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.single_scraper_seasons",
        new="scrapers.seasons_detail_scraper",
    ),
    ModuleNamingAlias(
        old="scrapers.single_scraper_grands_prix",
        new="scrapers.grands_prix_detail_scraper",
    ),
)


def module_naming_alias_map() -> dict[str, str]:
    return {entry.old: entry.new for entry in MODULE_NAMING_ALIASES}


__all__ = ["MODULE_NAMING_ALIASES", "ModuleNamingAlias", "module_naming_alias_map"]
