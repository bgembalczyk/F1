from dataclasses import dataclass
from typing import Any

from layers.seed.data_classes import RegistryValidationRule
from layers.seed.data_classes import RegistryValidationSpec
from layers.seed.registry.entries.entry import SeedRegistryEntry
from layers.seed.registry.entries.list_job import ListJobRegistryEntry
from layers.seed.registry.helpers import build_list_job_registry_entry_from_spec
from layers.seed.registry.helpers import build_raw_registry_spec
from layers.seed.registry.helpers import build_seed_registry_entry_from_spec
from layers.seed.registry.raw_specs import RawRegistrySpec
from scrapers.circuits.circuits_list_scraper import CircuitsListScraper
from scrapers.constructors_list_scraper import ConstructorsListScraper
from scrapers.drivers.fatalities_list_scraper_drivers import F1FatalitiesListScraper
from scrapers.drivers.female_drivers_list import FemaleDriversListScraper
from scrapers.drivers_list_scraper import DriversListScraper
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.engine_regulation import EngineRegulationScraper
from scrapers.engines.engine_restrictions import EngineRestrictionsScraper
from scrapers.grands_prix_list_scraper import GrandsPrixListScraper
from scrapers.points.points_scraper import PointsScraper
from scrapers.races.red_flagged_races_scraper.combined import RedFlaggedRacesScraper
from scrapers.seasons_list_scraper import SeasonsListScraper
from scrapers.sponsorship_liveries.scraper_sponsorship_liveries import F1SponsorshipLiveriesScraper
from scrapers.tyres.list_scraper_tyres import TyreManufacturersScraper
from scrapers.wiki.sources_registry_wiki import get_source_by_seed_name
from scrapers.wiki.sources_registry_wiki import resolve_seed_name
from scrapers.wiki.sources_registry_wiki import validate_sources_registry_consistency






LIST_SCRAPER_BY_SEED_NAME: dict[str, type[Any]] = {
    "circuits": CircuitsListScraper,
    "constructors_current": ConstructorsListScraper,
    "constructors_former": ConstructorsListScraper,
    "constructors_indianapolis_only": ConstructorsListScraper,
    "constructors_privateer": ConstructorsListScraper,
    "drivers": DriversListScraper,
    "drivers_female": FemaleDriversListScraper,
    "drivers_fatalities": F1FatalitiesListScraper,
    "seasons": SeasonsListScraper,
    "grands_prix_by_title": GrandsPrixListScraper,
    "engines_indianapolis_only": EngineManufacturersListScraper,
    "engines_restrictions": EngineRestrictionsScraper,
    "engines_regulations": EngineRegulationScraper,
    "engines_manufacturers": EngineManufacturersListScraper,
    "grands_prix_red_flagged_world_championship": RedFlaggedRacesScraper,
    "grands_prix_red_flagged_non_championship": RedFlaggedRacesScraper,
    "points_sprint": PointsScraper,
    "points_shortened": PointsScraper,
    "points_history": PointsScraper,
    "tyres": TyreManufacturersScraper,
    "sponsorship_liveries": F1SponsorshipLiveriesScraper,
}

SEED_FILENAME_OVERRIDES: dict[str, str] = {
    "circuits": "complete_circuits",
    "drivers": "complete_drivers",
    "seasons": "complete_seasons",
    "constructors": "complete_constructors",
    "grands_prix": "f1_grands_prix_extended.json",
}



RAW_REGISTRY_SPEC: tuple[RawRegistrySpec, ...] = build_raw_registry_spec()






LAYER_ONE_SEED_REGISTRY_ORDER: tuple[str, ...] = (
    "drivers",
    "constructors",
    "grands_prix",
    "circuits",
    "seasons",
)

seed_entries_by_name = {
    entry.seed_name: entry
    for entry in (
        build_seed_registry_entry_from_spec(spec) for spec in RAW_REGISTRY_SPEC
    )
    if entry is not None
}

EXPLICIT_LAYER_ONE_SEED_REGISTRY: tuple[SeedRegistryEntry, ...] = tuple(
    seed_entries_by_name[seed_name] for seed_name in LAYER_ONE_SEED_REGISTRY_ORDER
)


WIKI_LIST_JOB_REGISTRY: tuple[ListJobRegistryEntry, ...] = tuple(
    build_list_job_registry_entry_from_spec(spec)
    for spec in RAW_REGISTRY_SPEC
    if spec.include_in_list_registry
)


SEED_REGISTRY_VALIDATION_SPEC = RegistryValidationSpec(
    duplicate_message=lambda seed_name: f"Duplicate seed_name found: {seed_name}",
    empty_url_message=lambda seed_name: f"Seed '{seed_name}' has empty wikipedia_url",
    path_rules=(
        RegistryValidationRule(
            label="default_output_path",
            extractor=lambda entry: entry.default_output_path,
            expected_prefix=lambda entry: f"raw/{entry.output_category}/",
            message=lambda entry: (
                f"Seed '{entry.seed_name}' has inconsistent output path "
                f"'{entry.default_output_path}' for category '{entry.output_category}'"
            ),
        ),
        RegistryValidationRule(
            label="legacy_output_path",
            extractor=lambda entry: entry.legacy_output_path,
            expected_prefix=lambda entry: f"{entry.output_category}/",
            message=lambda entry: (
                f"Seed '{entry.seed_name}' has inconsistent legacy output path "
                f"'{entry.legacy_output_path}' for category '{entry.output_category}'"
            ),
        ),
    ),
)


LIST_JOB_REGISTRY_VALIDATION_SPEC = RegistryValidationSpec(
    duplicate_message=(
        lambda seed_name: f"Duplicate list seed_name found: {seed_name}"
    ),
    empty_url_message=(
        lambda seed_name: f"List seed '{seed_name}' has empty wikipedia_url"
    ),
    path_rules=(
        RegistryValidationRule(
            label="json_output_path",
            extractor=lambda entry: entry.json_output_path,
            expected_prefix=lambda entry: f"raw/{entry.output_category}/",
            message=lambda entry: (
                f"List seed '{entry.seed_name}' has inconsistent output path "
                f"'{entry.json_output_path}' for category '{entry.output_category}'"
            ),
        ),
        RegistryValidationRule(
            label="legacy_json_output_path",
            extractor=lambda entry: entry.legacy_json_output_path,
            expected_prefix=lambda entry: f"{entry.output_category}/",
            message=lambda entry: (
                f"List seed '{entry.seed_name}' has inconsistent legacy output path "
                f"'{entry.legacy_json_output_path}' "
                f"for category '{entry.output_category}'"
            ),
        ),
    ),
)
