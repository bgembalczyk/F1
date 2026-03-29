from dataclasses import dataclass
from typing import Any

from layers.seed.data_classes import RegistryValidationRule
from layers.seed.data_classes import RegistryValidationSpec
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from layers.types import DomainName
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


@dataclass(frozen=True)
class RawRegistrySpec:
    seed_name: str
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


def _seed_default_output_path(*, output_category: DomainName, filename: str) -> str:
    return f"raw/{output_category}/seeds/{filename}"


def _seed_legacy_output_path(*, output_category: DomainName, filename: str) -> str:
    return f"{output_category}/{filename}"


def _list_default_output_path(*, output_category: DomainName, filename: str) -> str:
    return f"raw/{output_category}/list/{filename}"


def _list_legacy_output_path(*, output_category: DomainName, filename: str) -> str:
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
        seed_name="circuits",
        list_scraper_cls=CircuitsListScraper,
        output_category=DomainName.CIRCUITS,
        list_filename="f1_circuits.json",
        seed_filename="complete_circuits",
    ),
    RawRegistrySpec(
        seed_name="constructors_current",
        list_scraper_cls=CurrentConstructorsListScraper,
        output_category=DomainName.CONSTRUCTORS,
        list_filename="f1_constructors_{year}.json",
    ),
    RawRegistrySpec(
        seed_name="constructors_former",
        list_scraper_cls=FormerConstructorsListScraper,
        output_category=DomainName.CHASSIS_CONSTRUCTORS,
        list_filename="f1_former_constructors.json",
    ),
    RawRegistrySpec(
        seed_name="constructors_indianapolis_only",
        list_scraper_cls=IndianapolisOnlyConstructorsListScraper,
        output_category=DomainName.CHASSIS_CONSTRUCTORS,
        list_filename="f1_indianapolis_only_constructors.json",
    ),
    RawRegistrySpec(
        seed_name="constructors_privateer",
        list_scraper_cls=PrivateerTeamsListScraper,
        output_category=DomainName.TEAMS,
        list_filename="f1_privateer_teams.json",
    ),
    RawRegistrySpec(
        seed_name="drivers",
        list_scraper_cls=F1DriversListScraper,
        output_category=DomainName.DRIVERS,
        list_filename="f1_drivers.json",
        seed_filename="complete_drivers",
    ),
    RawRegistrySpec(
        seed_name="drivers_female",
        list_scraper_cls=FemaleDriversListScraper,
        output_category=DomainName.DRIVERS,
        list_filename="female_drivers.json",
    ),
    RawRegistrySpec(
        seed_name="drivers_fatalities",
        list_scraper_cls=F1FatalitiesListScraper,
        output_category=DomainName.DRIVERS,
        list_filename="f1_driver_fatalities.json",
    ),
    RawRegistrySpec(
        seed_name="seasons",
        list_scraper_cls=SeasonsListScraper,
        output_category=DomainName.SEASONS,
        list_filename="f1_seasons.json",
        seed_filename="complete_seasons",
    ),
    RawRegistrySpec(
        seed_name="grands_prix_by_title",
        list_scraper_cls=GrandsPrixListScraper,
        output_category=DomainName.GRANDS_PRIX,
        list_filename="f1_grands_prix_by_title.json",
    ),
    RawRegistrySpec(
        seed_name="engines_indianapolis_only",
        list_scraper_cls=IndianapolisOnlyEngineManufacturersListScraper,
        output_category=DomainName.ENGINES,
        list_filename="f1_indianapolis_only_engine_manufacturers.json",
    ),
    RawRegistrySpec(
        seed_name="engines_restrictions",
        list_scraper_cls=EngineRestrictionsScraper,
        output_category=DomainName.RULES,
        list_filename="f1_engine_restrictions.json",
    ),
    RawRegistrySpec(
        seed_name="engines_regulations",
        list_scraper_cls=EngineRegulationScraper,
        output_category=DomainName.RULES,
        list_filename="f1_engine_regulations.json",
    ),
    RawRegistrySpec(
        seed_name="engines_manufacturers",
        list_scraper_cls=EngineManufacturersListScraper,
        output_category=DomainName.ENGINES,
        list_filename="f1_engine_manufacturers.json",
    ),
    RawRegistrySpec(
        seed_name="grands_prix_red_flagged_world_championship",
        list_scraper_cls=RedFlaggedWorldChampionshipRacesScraper,
        output_category=DomainName.RACES,
        list_filename="f1_red_flagged_world_championship_races.json",
    ),
    RawRegistrySpec(
        seed_name="grands_prix_red_flagged_non_championship",
        list_scraper_cls=RedFlaggedNonChampionshipRacesScraper,
        output_category=DomainName.RACES,
        list_filename="f1_red_flagged_non_championship_races.json",
    ),
    RawRegistrySpec(
        seed_name="points_sprint",
        list_scraper_cls=SprintQualifyingPointsScraper,
        output_category=DomainName.POINTS,
        list_filename="points_scoring_systems_sprint.json",
    ),
    RawRegistrySpec(
        seed_name="points_shortened",
        list_scraper_cls=ShortenedRacePointsScraper,
        output_category=DomainName.POINTS,
        list_filename="points_scoring_systems_shortened.json",
    ),
    RawRegistrySpec(
        seed_name="points_history",
        list_scraper_cls=PointsScoringSystemsHistoryScraper,
        output_category=DomainName.POINTS,
        list_filename="points_scoring_systems_history.json",
    ),
    RawRegistrySpec(
        seed_name="tyres",
        list_scraper_cls=TyreManufacturersBySeasonScraper,
        output_category=DomainName.SEASONS,
        list_filename="f1_tyre_manufacturers_by_season.json",
    ),
    RawRegistrySpec(
        seed_name="sponsorship_liveries",
        list_scraper_cls=F1SponsorshipLiveriesScraper,
        output_category=DomainName.TEAMS,
        list_filename="f1_sponsorship_liveries.json",
    ),
    RawRegistrySpec(
        seed_name="constructors",
        list_scraper_cls=CurrentConstructorsListScraper,
        output_category=DomainName.CONSTRUCTORS,
        list_filename="f1_constructors_{year}.json",
        seed_filename="complete_constructors",
        include_in_list_registry=False,
    ),
    RawRegistrySpec(
        seed_name="grands_prix",
        list_scraper_cls=GrandsPrixListScraper,
        output_category=DomainName.GRANDS_PRIX,
        list_filename="f1_grands_prix_by_title.json",
        seed_filename="f1_grands_prix_extended.json",
        include_in_list_registry=False,
    ),
)


_LAYER_ONE_SEED_REGISTRY_ORDER: tuple[DomainName, ...] = (
    DomainName.DRIVERS,
    DomainName.CONSTRUCTORS,
    DomainName.GRANDS_PRIX,
    DomainName.CIRCUITS,
    DomainName.SEASONS,
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
