from dataclasses import dataclass
from typing import Any

from layers.seed.data_classes import RegistryValidationRule
from layers.seed.data_classes import RegistryValidationSpec
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from layers.seed.registry.types import DomainName
from layers.seed.registry.types import SeedName
from scrapers.circuits.list_scraper import CircuitsListScraper
from scrapers.constructors.constructors_list import ConstructorsListScraper
from scrapers.drivers.fatalities_list_scraper import F1FatalitiesListScraper
from scrapers.drivers.female_drivers_list import FemaleDriversListScraper
from scrapers.drivers.list_scraper import F1DriversListScraper
from scrapers.engines.engine_manufacturers_list import EngineManufacturersListScraper
from scrapers.engines.engine_regulation import EngineRegulationScraper
from scrapers.engines.engine_restrictions import EngineRestrictionsScraper
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper
from scrapers.grands_prix.red_flagged_races_scraper.combined import (
    RedFlaggedRacesScraper,
)
from scrapers.points.points_scraper import PointsScraper
from scrapers.seasons.list_scraper import SeasonsListScraper
from scrapers.sponsorship_liveries.scraper import F1SponsorshipLiveriesScraper
from scrapers.tyres.list_scraper import TyreManufacturersScraper


@dataclass(frozen=True)
class RawRegistrySpec:
    seed_name: SeedName
    list_scraper_cls: type[Any]
    output_category: DomainName
    list_filename: str
    seed_filename: str | None = None
    seed_output_category: DomainName | None = None
    list_output_category: DomainName | None = None
    include_in_list_registry: bool = True


def _resolve_wikipedia_url(list_scraper_cls: type[Any]) -> str:
    config = getattr(list_scraper_cls, "CONFIG", None)
    if config is not None and hasattr(config, "url"):
        return config.url

    url = getattr(list_scraper_cls, "url", None)
    if isinstance(url, str):
        return url

    msg = f"Cannot resolve wikipedia_url for scraper '{list_scraper_cls.__name__}'"
    raise ValueError(msg)


def _seed_default_output_path(*, output_category: str, filename: str) -> str:
    return f"raw/{output_category}/seeds/{filename}"


def _seed_legacy_output_path(*, output_category: str, filename: str) -> str:
    return f"{output_category}/{filename}"


def _list_default_output_path(*, output_category: str, filename: str) -> str:
    return f"raw/{output_category}/list/{filename}"


def _list_legacy_output_path(*, output_category: str, filename: str) -> str:
    return f"{output_category}/{filename}"


def build_seed_registry_entry_from_spec(spec: RawRegistrySpec) -> SeedRegistryEntry | None:
    if spec.seed_filename is None:
        return None

    output_category = spec.seed_output_category or spec.output_category
    return SeedRegistryEntry(
        seed_name=spec.seed_name,
        wikipedia_url=_resolve_wikipedia_url(spec.list_scraper_cls),
        output_category=output_category,
        list_scraper_cls=spec.list_scraper_cls,
        default_output_path=_seed_default_output_path(
            output_category=output_category,
            filename=spec.seed_filename,
        ),
        legacy_output_path=_seed_legacy_output_path(
            output_category=output_category,
            filename=spec.seed_filename,
        ),
    )


def build_list_job_registry_entry_from_spec(spec: RawRegistrySpec) -> ListJobRegistryEntry:
    output_category = spec.list_output_category or spec.output_category
    return ListJobRegistryEntry(
        seed_name=spec.seed_name,
        wikipedia_url=_resolve_wikipedia_url(spec.list_scraper_cls),
        output_category=output_category,
        list_scraper_cls=spec.list_scraper_cls,
        json_output_path=_list_default_output_path(
            output_category=output_category,
            filename=spec.list_filename,
        ),
        legacy_json_output_path=_list_legacy_output_path(
            output_category=output_category,
            filename=spec.list_filename,
        ),
    )


RAW_REGISTRY_SPEC: tuple[RawRegistrySpec, ...] = (
    RawRegistrySpec(
        seed_name=SeedName.CIRCUITS,
        list_scraper_cls=CircuitsListScraper,
        output_category=DomainName.CIRCUITS,
        list_filename="f1_circuits.json",
        seed_filename="complete_circuits",
    ),
    RawRegistrySpec(
        seed_name=SeedName.CONSTRUCTORS_CURRENT,
        list_scraper_cls=ConstructorsListScraper,
        output_category=DomainName.CONSTRUCTORS,
        list_filename="f1_constructors_{year}.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.CONSTRUCTORS_FORMER,
        list_scraper_cls=ConstructorsListScraper,
        output_category=DomainName.CHASSIS_CONSTRUCTORS,
        list_filename="f1_former_constructors.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.CONSTRUCTORS_INDIANAPOLIS_ONLY,
        list_scraper_cls=ConstructorsListScraper,
        output_category=DomainName.CHASSIS_CONSTRUCTORS,
        list_filename="f1_indianapolis_only_constructors.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.CONSTRUCTORS_PRIVATEER,
        list_scraper_cls=ConstructorsListScraper,
        output_category=DomainName.TEAMS,
        list_filename="f1_privateer_teams.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.DRIVERS,
        list_scraper_cls=F1DriversListScraper,
        output_category=DomainName.DRIVERS,
        list_filename="f1_drivers.json",
        seed_filename="complete_drivers",
    ),
    RawRegistrySpec(
        seed_name=SeedName.DRIVERS_FEMALE,
        list_scraper_cls=FemaleDriversListScraper,
        output_category=DomainName.DRIVERS,
        list_filename="female_drivers.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.DRIVERS_FATALITIES,
        list_scraper_cls=F1FatalitiesListScraper,
        output_category=DomainName.DRIVERS,
        list_filename="f1_driver_fatalities.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.SEASONS,
        list_scraper_cls=SeasonsListScraper,
        output_category=DomainName.SEASONS,
        list_filename="f1_seasons.json",
        seed_filename="complete_seasons",
    ),
    RawRegistrySpec(
        seed_name=SeedName.GRANDS_PRIX_BY_TITLE,
        list_scraper_cls=GrandsPrixListScraper,
        output_category=DomainName.GRANDS_PRIX,
        list_filename="f1_grands_prix_by_title.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.ENGINES_INDIANAPOLIS_ONLY,
        list_scraper_cls=EngineManufacturersListScraper,
        output_category=DomainName.ENGINES,
        list_filename="f1_indianapolis_only_engine_manufacturers.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.ENGINES_RESTRICTIONS,
        list_scraper_cls=EngineRestrictionsScraper,
        output_category=DomainName.RULES,
        list_filename="f1_engine_restrictions.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.ENGINES_REGULATIONS,
        list_scraper_cls=EngineRegulationScraper,
        output_category=DomainName.RULES,
        list_filename="f1_engine_regulations.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.ENGINES_MANUFACTURERS,
        list_scraper_cls=EngineManufacturersListScraper,
        output_category=DomainName.ENGINES,
        list_filename="f1_engine_manufacturers.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.GRANDS_PRIX_RED_FLAGGED_WORLD_CHAMPIONSHIP,
        list_scraper_cls=RedFlaggedRacesScraper,
        output_category=DomainName.RACES,
        list_filename="f1_red_flagged_world_championship_races.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.GRANDS_PRIX_RED_FLAGGED_NON_CHAMPIONSHIP,
        list_scraper_cls=RedFlaggedRacesScraper,
        output_category=DomainName.RACES,
        list_filename="f1_red_flagged_non_championship_races.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.POINTS_SPRINT,
        list_scraper_cls=PointsScraper,
        output_category=DomainName.POINTS,
        list_filename="points_scoring_systems_sprint.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.POINTS_SHORTENED,
        list_scraper_cls=PointsScraper,
        output_category=DomainName.POINTS,
        list_filename="points_scoring_systems_shortened.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.POINTS_HISTORY,
        list_scraper_cls=PointsScraper,
        output_category=DomainName.POINTS,
        list_filename="points_scoring_systems_history.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.TYRES,
        list_scraper_cls=TyreManufacturersScraper,
        output_category=DomainName.SEASONS,
        list_filename="f1_tyre_manufacturers_by_season.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.SPONSORSHIP_LIVERIES,
        list_scraper_cls=F1SponsorshipLiveriesScraper,
        output_category=DomainName.TEAMS,
        list_filename="f1_sponsorship_liveries.json",
    ),
    RawRegistrySpec(
        seed_name=SeedName.CONSTRUCTORS,
        list_scraper_cls=ConstructorsListScraper,
        output_category=DomainName.CONSTRUCTORS,
        list_filename="f1_constructors_{year}.json",
        seed_filename="complete_constructors",
        include_in_list_registry=False,
    ),
    RawRegistrySpec(
        seed_name=SeedName.GRANDS_PRIX,
        list_scraper_cls=GrandsPrixListScraper,
        output_category=DomainName.GRANDS_PRIX,
        list_filename="f1_grands_prix_by_title.json",
        seed_filename="f1_grands_prix_extended.json",
        include_in_list_registry=False,
    ),
)


_LAYER_ONE_SEED_REGISTRY_ORDER: tuple[SeedName, ...] = (
    SeedName.DRIVERS,
    SeedName.CONSTRUCTORS,
    SeedName.GRANDS_PRIX,
    SeedName.CIRCUITS,
    SeedName.SEASONS,
)

_seed_entries_by_name = {
    entry.seed_name: entry
    for entry in (
        build_seed_registry_entry_from_spec(spec) for spec in RAW_REGISTRY_SPEC
    )
    if entry is not None
}

EXPLICIT_LAYER_ONE_SEED_REGISTRY: tuple[SeedRegistryEntry, ...] = tuple(
    _seed_entries_by_name[seed_name] for seed_name in _LAYER_ONE_SEED_REGISTRY_ORDER
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
