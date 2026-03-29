"""Single source of truth for core domain entrypoint/orchestration metadata."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile

if TYPE_CHECKING:
    from collections.abc import Callable

    from scrapers.base.run_config import RunConfig


RunnerKind = Literal["class", "function_export"]


@dataclass(frozen=True)
class RunnerMetadata:
    """Metadata needed to build a layer-one runner for a domain."""

    kind: RunnerKind
    target_path: str
    component_metadata: dict[str, str] | None = None


@dataclass(frozen=True)
class DomainRegistryEntry:
    """Canonical metadata shared across domain entrypoints and orchestration."""

    domain: str
    scraper_path: str
    default_output_json: str | Path
    run_profile_name: RunProfileName
    runner: RunnerMetadata
    default_output_csv: str | Path | None = None


def strict_quality_profile() -> RunConfig:
    return build_run_profile(RunProfileName.STRICT)


def minimal_profile() -> RunConfig:
    return build_run_profile(RunProfileName.MINIMAL)


def minimal_debug_profile() -> RunConfig:
    return build_run_profile(RunProfileName.DEBUG)


_PROFILE_FACTORIES: dict[RunProfileName, Callable[[], RunConfig]] = {
    RunProfileName.STRICT: strict_quality_profile,
    RunProfileName.MINIMAL: minimal_profile,
    RunProfileName.DEBUG: minimal_debug_profile,
}


def run_config_profile_for(name: RunProfileName) -> Callable[[], RunConfig]:
    return _PROFILE_FACTORIES[name]


DOMAIN_REGISTRY: dict[str, DomainRegistryEntry] = {
    "drivers": DomainRegistryEntry(
        domain="drivers",
        scraper_path="scrapers.drivers.list_scraper:F1DriversListScraper",
        default_output_json="drivers/f1_drivers.json",
        run_profile_name=RunProfileName.STRICT,
        runner=RunnerMetadata(
            kind="function_export",
            target_path="scrapers.drivers.helpers.export:export_complete_drivers",
            component_metadata={
                "domain": "drivers",
                "seed_name": "drivers",
                "layer": "layer_one",
                "output_category": "drivers",
                "component_type": "runner",
            },
        ),
    ),
    "seasons": DomainRegistryEntry(
        domain="seasons",
        scraper_path="scrapers.seasons.list_scraper:SeasonsListScraper",
        default_output_json="seasons/f1_seasons.json",
        default_output_csv="seasons/f1_seasons.csv",
        run_profile_name=RunProfileName.MINIMAL,
        runner=RunnerMetadata(
            kind="function_export",
            target_path="scrapers.seasons.helpers:export_complete_seasons",
            component_metadata={
                "domain": "seasons",
                "seed_name": "seasons",
                "layer": "layer_one",
                "output_category": "seasons",
                "component_type": "runner",
            },
        ),
    ),
    "grands_prix": DomainRegistryEntry(
        domain="grands_prix",
        scraper_path="scrapers.grands_prix.list_scraper:GrandsPrixListScraper",
        default_output_json="grands_prix/f1_grands_prix_by_title.json",
        default_output_csv="grands_prix/f1_grands_prix_by_title.csv",
        run_profile_name=RunProfileName.MINIMAL,
        runner=RunnerMetadata(
            kind="class",
            target_path="layers.orchestration.runners.grand_prix:GrandPrixRunner",
            component_metadata={
                "domain": "grands_prix",
                "seed_name": "grands_prix",
                "layer": "layer_one",
                "output_category": "grands_prix",
                "component_type": "runner",
            },
        ),
    ),
    "circuits": DomainRegistryEntry(
        domain="circuits",
        scraper_path="scrapers.circuits.list_scraper:CircuitsListScraper",
        default_output_json="circuits/f1_circuits.json",
        default_output_csv="circuits/f1_circuits.csv",
        run_profile_name=RunProfileName.STRICT,
        runner=RunnerMetadata(
            kind="function_export",
            target_path="scrapers.circuits.helpers.export:export_complete_circuits",
            component_metadata={
                "domain": "circuits",
                "seed_name": "circuits",
                "layer": "layer_one",
                "output_category": "circuits",
                "component_type": "runner",
            },
        ),
    ),
    "constructors": DomainRegistryEntry(
        domain="constructors",
        scraper_path=(
            "scrapers.constructors.current_constructors_list:"
            "CurrentConstructorsListScraper"
        ),
        default_output_json="constructors/f1_constructors_{year}.json",
        default_output_csv="constructors/f1_constructors_{year}.csv",
        run_profile_name=RunProfileName.DEBUG,
        runner=RunnerMetadata(
            kind="function_export",
            target_path="scrapers.constructors.helpers.export:export_complete_constructors",
            component_metadata={
                "domain": "constructors",
                "seed_name": "constructors",
                "layer": "layer_one",
                "output_category": "constructors",
                "component_type": "runner",
            },
        ),
    ),
}


def import_target(path: str) -> object:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, attr_name)


def get_domain_registry_entry(domain: str) -> DomainRegistryEntry:
    return DOMAIN_REGISTRY[domain]


@cache
def get_registry_year() -> int | None:
    return getattr(import_module("scrapers.constructors.constants"), "CURRENT_YEAR", None)


def render_registry_output_path(
    *,
    domain: str,
    path: str | Path | None,
) -> str | Path | None:
    if path is None:
        return None
    current_year = get_registry_year() if domain == "constructors" else None
    if current_year is None:
        return path
    if isinstance(path, Path):
        return Path(str(path).format(year=current_year))
    return path.format(year=current_year)


def get_domain_entrypoint_scraper_metadata() -> dict[str, str]:
    return {domain: entry.scraper_path for domain, entry in DOMAIN_REGISTRY.items()}
