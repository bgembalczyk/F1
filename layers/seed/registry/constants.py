from dataclasses import dataclass
from typing import Any

from layers.seed.data_classes import RegistryValidationRule
from layers.seed.data_classes import RegistryValidationSpec
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.circuits import CircuitsListScraper
from scrapers.constructors import ConstructorsListScraper
from scrapers.drivers import F1FatalitiesListScraper
from scrapers.drivers import FemaleDriversListScraper
from scrapers.drivers import F1DriversListScraper
from scrapers.engines import EngineManufacturersListScraper
from scrapers.engines import EngineRegulationScraper
from scrapers.engines import EngineRestrictionsScraper
from scrapers.grands_prix import GrandsPrixListScraper
from scrapers.grands_prix.red_flagged_races_scraper.combined import (
    RedFlaggedRacesScraper,
)
from scrapers.points import PointsScraper
from scrapers.seasons import SeasonsListScraper
from scrapers.sponsorship_liveries import F1SponsorshipLiveriesScraper
from scrapers.tyres.list_scraper import TyreManufacturersScraper
from scrapers.wiki.sources_registry import get_source_by_seed_name
from scrapers.wiki.sources_registry import resolve_seed_name
from scrapers.wiki.sources_registry import validate_sources_registry_consistency


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


_LIST_SCRAPER_BY_SEED_NAME: dict[str, type[Any]] = {
    "circuits": CircuitsListScraper,
    "constructors_current": ConstructorsListScraper,
    "constructors_former": ConstructorsListScraper,
    "constructors_indianapolis_only": ConstructorsListScraper,
    "constructors_privateer": ConstructorsListScraper,
    "drivers": F1DriversListScraper,
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

_SEED_FILENAME_OVERRIDES: dict[str, str] = {
    "circuits": "complete_circuits",
    "drivers": "complete_drivers",
    "seasons": "complete_seasons",
    "constructors": "complete_constructors",
    "grands_prix": "f1_grands_prix_extended.json",
}


def _validate_seed_name_consistency_at_startup() -> None:
    validate_sources_registry_consistency()

    resolved_seed_names: set[str] = set()
    for configured_seed_name in _LIST_SCRAPER_BY_SEED_NAME:
        canonical_seed_name = resolve_seed_name(configured_seed_name, warn=False)
        get_source_by_seed_name(canonical_seed_name, warn=False)
        if canonical_seed_name in resolved_seed_names:
            msg = (
                "Duplicate canonical seed_name in _LIST_SCRAPER_BY_SEED_NAME "
                f"after legacy alias resolution: {canonical_seed_name!r}"
            )
            raise ValueError(msg)
        resolved_seed_names.add(canonical_seed_name)

    for configured_seed_name in _SEED_FILENAME_OVERRIDES:
        get_source_by_seed_name(configured_seed_name, warn=False)


def _build_raw_registry_spec() -> tuple[RawRegistrySpec, ...]:
    _validate_seed_name_consistency_at_startup()

    specs: list[RawRegistrySpec] = []
    for seed_name, list_scraper_cls in _LIST_SCRAPER_BY_SEED_NAME.items():
        source = get_source_by_seed_name(seed_name, warn=False)
        specs.append(
            RawRegistrySpec(
                seed_name=source.seed_name,
                list_scraper_cls=list_scraper_cls,
                output_category=source.output_category,
                list_filename=source.list_filename,
                seed_filename=_SEED_FILENAME_OVERRIDES.get(source.seed_name),
            ),
        )

    constructors_source = get_source_by_seed_name("constructors", warn=False)
    specs.append(
        RawRegistrySpec(
            seed_name="constructors",
            list_scraper_cls=ConstructorsListScraper,
            output_category=constructors_source.output_category,
            list_filename=constructors_source.list_filename,
            seed_filename=_SEED_FILENAME_OVERRIDES["constructors"],
            include_in_list_registry=False,
        ),
    )

    grands_prix_source = get_source_by_seed_name("grands_prix", warn=False)
    specs.append(
        RawRegistrySpec(
            seed_name="grands_prix",
            list_scraper_cls=GrandsPrixListScraper,
            output_category=grands_prix_source.output_category,
            list_filename=grands_prix_source.list_filename,
            seed_filename=_SEED_FILENAME_OVERRIDES["grands_prix"],
            include_in_list_registry=False,
        ),
    )
    return tuple(specs)


RAW_REGISTRY_SPEC: tuple[RawRegistrySpec, ...] = _build_raw_registry_spec()


def _validate_registry_startup_consistency() -> None:
    for spec in RAW_REGISTRY_SPEC:
        source = get_source_by_seed_name(spec.seed_name, warn=False)
        if spec.output_category != source.output_category:
            msg = (
                "Seed registry startup consistency check failed for output_category: "
                f"{spec.seed_name!r} -> {spec.output_category!r} "
                f"(expected {source.output_category!r})"
            )
            raise ValueError(msg)
        if spec.list_filename != source.list_filename:
            msg = (
                "Seed registry startup consistency check failed for list_filename: "
                f"{spec.seed_name!r} -> {spec.list_filename!r} "
                f"(expected {source.list_filename!r})"
            )
            raise ValueError(msg)


_validate_registry_startup_consistency()


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
