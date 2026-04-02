from dataclasses import dataclass
from typing import Any

from layers.seed.data_classes import RegistryValidationRule
from layers.seed.data_classes import RegistryValidationSpec
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
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
from scrapers.wiki.constants import DRIVER_FATALITIES_SOURCE
from scrapers.wiki.constants import F1_DRIVERS_SOURCE
from scrapers.wiki.constants import F1_ENGINE_MANUFACTURERS_SOURCE
from scrapers.wiki.constants import F1_INDIANAPOLIS_ONLY_ENGINE_MANUFACTURERS_SOURCE
from scrapers.wiki.constants import F1_RED_FLAGGED_NON_CHAMPIONSHIP_SOURCE
from scrapers.wiki.constants import F1_RED_FLAGGED_WORLD_CHAMPIONSHIP_SOURCE
from scrapers.wiki.constants import FEMALE_DRIVERS_SOURCE
from scrapers.wiki.constants import FORMER_CONSTRUCTORS_SOURCE
from scrapers.wiki.constants import INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE
from scrapers.wiki.constants import PRIVATEER_TEAMS_SOURCE
from scrapers.wiki.constants import SPONSORSHIP_LIVERIES_SOURCE
from scrapers.wiki.constants import TYRE_MANUFACTURERS_SOURCE


@dataclass(frozen=True)
class RawRegistrySpec:
    seed_name: str
    list_scraper_cls: type[Any]
    output_category: str
    list_filename: str
    seed_filename: str | None = None
    seed_output_category: str | None = None
    list_output_category: str | None = None
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


def build_seed_registry_entry_from_spec(
    spec: RawRegistrySpec,
) -> SeedRegistryEntry | None:
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


def build_list_job_registry_entry_from_spec(
    spec: RawRegistrySpec,
) -> ListJobRegistryEntry:
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
        output_category="circuits",
        list_filename="f1_circuits.json",
        seed_filename="complete_circuits",
    ),
    RawRegistrySpec(
        seed_name="constructors_current",
        list_scraper_cls=ConstructorsListScraper,
        output_category="constructors",
        list_filename="f1_constructors_{year}.json",
    ),
    RawRegistrySpec(
        seed_name="constructors_former",
        list_scraper_cls=ConstructorsListScraper,
        output_category="chassis_constructors",
        list_filename=FORMER_CONSTRUCTORS_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="constructors_indianapolis_only",
        list_scraper_cls=ConstructorsListScraper,
        output_category="chassis_constructors",
        list_filename=INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="constructors_privateer",
        list_scraper_cls=ConstructorsListScraper,
        output_category="teams",
        list_filename=PRIVATEER_TEAMS_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="drivers",
        list_scraper_cls=F1DriversListScraper,
        output_category="drivers",
        list_filename=F1_DRIVERS_SOURCE,
        seed_filename="complete_drivers",
    ),
    RawRegistrySpec(
        seed_name="drivers_female",
        list_scraper_cls=FemaleDriversListScraper,
        output_category="drivers",
        list_filename=FEMALE_DRIVERS_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="drivers_fatalities",
        list_scraper_cls=F1FatalitiesListScraper,
        output_category="drivers",
        list_filename=DRIVER_FATALITIES_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="seasons",
        list_scraper_cls=SeasonsListScraper,
        output_category="seasons",
        list_filename="f1_seasons.json",
        seed_filename="complete_seasons",
    ),
    RawRegistrySpec(
        seed_name="grands_prix_by_title",
        list_scraper_cls=GrandsPrixListScraper,
        output_category="grands_prix",
        list_filename="f1_grands_prix_by_title.json",
    ),
    RawRegistrySpec(
        seed_name="engines_indianapolis_only",
        list_scraper_cls=EngineManufacturersListScraper,
        output_category="engines",
        list_filename=F1_INDIANAPOLIS_ONLY_ENGINE_MANUFACTURERS_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="engines_restrictions",
        list_scraper_cls=EngineRestrictionsScraper,
        output_category="rules",
        list_filename="f1_engine_restrictions.json",
    ),
    RawRegistrySpec(
        seed_name="engines_regulations",
        list_scraper_cls=EngineRegulationScraper,
        output_category="rules",
        list_filename="f1_engine_regulations.json",
    ),
    RawRegistrySpec(
        seed_name="engines_manufacturers",
        list_scraper_cls=EngineManufacturersListScraper,
        output_category="engines",
        list_filename=F1_ENGINE_MANUFACTURERS_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="grands_prix_red_flagged_world_championship",
        list_scraper_cls=RedFlaggedRacesScraper,
        output_category="races",
        list_filename=F1_RED_FLAGGED_WORLD_CHAMPIONSHIP_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="grands_prix_red_flagged_non_championship",
        list_scraper_cls=RedFlaggedRacesScraper,
        output_category="races",
        list_filename=F1_RED_FLAGGED_NON_CHAMPIONSHIP_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="points_sprint",
        list_scraper_cls=PointsScraper,
        output_category="points",
        list_filename="points_scoring_systems_sprint.json",
    ),
    RawRegistrySpec(
        seed_name="points_shortened",
        list_scraper_cls=PointsScraper,
        output_category="points",
        list_filename="points_scoring_systems_shortened.json",
    ),
    RawRegistrySpec(
        seed_name="points_history",
        list_scraper_cls=PointsScraper,
        output_category="points",
        list_filename="points_scoring_systems_history.json",
    ),
    RawRegistrySpec(
        seed_name="tyres",
        list_scraper_cls=TyreManufacturersScraper,
        output_category="seasons",
        list_filename=TYRE_MANUFACTURERS_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="sponsorship_liveries",
        list_scraper_cls=F1SponsorshipLiveriesScraper,
        output_category="teams",
        list_filename=SPONSORSHIP_LIVERIES_SOURCE,
    ),
    RawRegistrySpec(
        seed_name="constructors",
        list_scraper_cls=ConstructorsListScraper,
        output_category="constructors",
        list_filename="f1_constructors_{year}.json",
        seed_filename="complete_constructors",
        include_in_list_registry=False,
    ),
    RawRegistrySpec(
        seed_name="grands_prix",
        list_scraper_cls=GrandsPrixListScraper,
        output_category="grands_prix",
        list_filename="f1_grands_prix_by_title.json",
        seed_filename="f1_grands_prix_extended.json",
        include_in_list_registry=False,
    ),
)


_LAYER_ONE_SEED_REGISTRY_ORDER: tuple[str, ...] = (
    "drivers",
    "constructors",
    "grands_prix",
    "circuits",
    "seasons",
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
