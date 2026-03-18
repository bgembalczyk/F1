from collections.abc import Callable
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from layers.seed.data_classes import RegistryValidationRule
from layers.seed.data_classes import RegistryValidationSpec
from layers.seed.registry.constants import EXPLICIT_LAYER_ONE_SEED_REGISTRY
from layers.seed.registry.constants import LIST_JOB_REGISTRY_VALIDATION_SPEC
from layers.seed.registry.constants import SEED_REGISTRY_VALIDATION_SPEC
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.constructors.current_constructors_list import (
    CurrentConstructorsListScraper,
)
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.drivers.fatalities_list_scraper import F1FatalitiesListScraper
from scrapers.drivers.female_drivers_list import FemaleDriversListScraper
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.engine_regulation import EngineRegulationScraper
from scrapers.engines.engine_restrictions import EngineRestrictionsScraper
from scrapers.engines.indianapolis_only_engine_manufacturers_list import (
    IndianapolisOnlyEngineManufacturersListScraper,
)
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.red_flagged_races_scraper.non_championship import (
    RedFlaggedNonChampionshipRacesScraper,
)
from scrapers.grands_prix.red_flagged_races_scraper.world_championship import (
    RedFlaggedWorldChampionshipRacesScraper,
)
from scrapers.points.points_scoring_systems_history import (
    PointsScoringSystemsHistoryScraper,
)
from scrapers.points.shortened_race_points import ShortenedRacePointsScraper
from scrapers.points.sprint_qualifying_points import SprintQualifyingPointsScraper
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.sponsorship_liveries.scraper import F1SponsorshipLiveriesScraper
from scrapers.tyres.list_scraper import TyreManufacturersBySeasonScraper
from scrapers.wiki.discovery import discover_layer_one_seed_components


def _seed_entry_from_component(
    *,
    seed_name: str,
    component: Any,
    default_output_path: str,
    legacy_output_path: str,
) -> SeedRegistryEntry:
    metadata = component.metadata
    return SeedRegistryEntry(
        seed_name=seed_name,
        wikipedia_url=component.cls.CONFIG.url,
        output_category=metadata.output_category,
        list_scraper_cls=component.cls,
        default_output_path=default_output_path,
        legacy_output_path=legacy_output_path,
    )


def _validate_registry_entry(
    *,
    entry: Any,
    spec: RegistryValidationSpec,
    seen_seed_names: set[str],
) -> None:
    _validate_unique_seed_name(
        seed_name=entry.seed_name,
        seen_seed_names=seen_seed_names,
        duplicate_message=spec.duplicate_message,
    )
    _validate_wikipedia_url(
        seed_name=entry.seed_name,
        wikipedia_url=entry.wikipedia_url,
        message=spec.empty_url_message,
    )
    for rule in spec.path_rules:
        _validate_path_prefix(entry=entry, rule=rule)


def _build_discovered_layer_one_seed_registry() -> tuple[SeedRegistryEntry, ...]:
    discovered = discover_layer_one_seed_components()
    explicit_by_seed = {
        entry.seed_name: entry for entry in EXPLICIT_LAYER_ONE_SEED_REGISTRY
    }
    registry: list[SeedRegistryEntry] = []

    for seed_name, explicit in explicit_by_seed.items():
        component = discovered.get(seed_name)
        if component is None:
            registry.append(explicit)
            continue

        metadata = component.metadata
        if metadata.output_category != explicit.output_category:
            msg = (
                f"Conflicting output_category for seed '{seed_name}': "
                "explicit='"
                f"{explicit.output_category}' discovered='{metadata.output_category}'"
            )
            raise ValueError(msg)
        registry.append(
            _seed_entry_from_component(
                seed_name=metadata.seed_name,
                component=component,
                default_output_path=metadata.default_output_path
                or explicit.default_output_path,
                legacy_output_path=metadata.legacy_output_path
                or explicit.legacy_output_path,
            ),
        )

    for seed_name, component in discovered.items():
        if seed_name in explicit_by_seed:
            continue
        metadata = component.metadata
        if not metadata.default_output_path or not metadata.legacy_output_path:
            msg = (
                f"Discovered layer-one seed '{seed_name}' "
                "is missing output paths in metadata"
            )
            raise ValueError(msg)
        registry.append(
            _seed_entry_from_component(
                seed_name=seed_name,
                component=component,
                default_output_path=metadata.default_output_path,
                legacy_output_path=metadata.legacy_output_path,
            ),
        )

    return tuple(registry)


WIKI_SEED_REGISTRY: tuple[SeedRegistryEntry, ...] = (
    _build_discovered_layer_one_seed_registry()
)

def _validate_unique_seed_name(
    *,
    seed_name: str,
    seen_seed_names: set[str],
    duplicate_message: Callable[[str], str],
) -> None:
    if seed_name in seen_seed_names:
        msg = duplicate_message(seed_name)
        raise ValueError(msg)
    seen_seed_names.add(seed_name)


def _validate_wikipedia_url(
    *,
    seed_name: str,
    wikipedia_url: str,
    message: Callable[[str], str],
) -> None:
    if not wikipedia_url.strip():
        msg = message(seed_name)
        raise ValueError(msg)


def _validate_path_prefix(*, entry: Any, rule: RegistryValidationRule) -> None:
    output_path = rule.extractor(entry)
    prefix = rule.expected_prefix(entry)
    if not output_path.startswith(prefix):
        msg = rule.message(entry)
        raise ValueError(msg)


def _validate_registry(
    *,
    registry: tuple[Any, ...],
    spec: RegistryValidationSpec,
) -> None:
    seen_seed_names: set[str] = set()

    for entry in registry:
        _validate_registry_entry(
            entry=entry,
            spec=spec,
            seen_seed_names=seen_seed_names,
        )


def validate_seed_registry(
    registry: tuple[SeedRegistryEntry, ...] = WIKI_SEED_REGISTRY,
) -> None:
    _validate_registry(registry=registry, spec=SEED_REGISTRY_VALIDATION_SPEC)


def validate_list_job_registry(
    registry: tuple[ListJobRegistryEntry, ...] = WIKI_LIST_JOB_REGISTRY,
) -> None:
    _validate_registry(registry=registry, spec=LIST_JOB_REGISTRY_VALIDATION_SPEC)


