from collections.abc import Callable
from functools import lru_cache
from typing import Any

from layers.seed.data_classes import RegistryValidationRule
from layers.seed.data_classes import RegistryValidationSpec
from layers.seed.registry.constants import EXPLICIT_LAYER_ONE_SEED_REGISTRY
from layers.seed.registry.constants import LIST_JOB_REGISTRY_VALIDATION_SPEC
from layers.seed.registry.constants import LIST_SCRAPER_BY_SEED_NAME
from layers.seed.registry.constants import RAW_REGISTRY_SPEC
from layers.seed.registry.constants import SEED_FILENAME_OVERRIDES
from layers.seed.registry.constants import SEED_REGISTRY_VALIDATION_SPEC
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.entries.base import BaseRegistryEntry
from layers.seed.registry.entries.entry import SeedRegistryEntry
from layers.seed.registry.entries.list_job import ListJobRegistryEntry
from layers.seed.registry.raw_specs import RawRegistrySpec
from scrapers.constructors import ConstructorsListScraper
from scrapers.grands_prix.list_scraper_grands_prix import GrandsPrixListScraper
from scrapers.wiki.discovery_wiki import discover_layer_one_seed_components
from scrapers.wiki.sources_registry_wiki import get_source_by_seed_name
from scrapers.wiki.sources_registry_wiki import resolve_seed_name
from scrapers.wiki.sources_registry_wiki import validate_sources_registry_consistency


def seed_entry_from_component(
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


def validate_registry_entry(
    *,
    entry: BaseRegistryEntry,
    spec: RegistryValidationSpec,
    seen_seed_names: set[str],
) -> None:
    validate_unique_seed_name(
        seed_name=entry.seed_name,
        seen_seed_names=seen_seed_names,
        duplicate_message=spec.duplicate_message,
    )
    validate_wikipedia_url(
        seed_name=entry.seed_name,
        wikipedia_url=entry.wikipedia_url,
        message=spec.empty_url_message,
    )
    for rule in spec.path_rules:
        validate_path_prefix(entry=entry, rule=rule)


def build_discovered_layer_one_seed_registry() -> tuple[SeedRegistryEntry, ...]:
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
            seed_entry_from_component(
                seed_name=metadata.seed_name,
                component=component,
                default_output_path=metadata.default_output_path
                or explicit.default_output_path,
                legacy_output_path=metadata.legacy_output_path
                or explicit.legacy_output_path,
            ),
        )

    for seed_name in sorted(discovered):
        component = discovered[seed_name]
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
            seed_entry_from_component(
                seed_name=seed_name,
                component=component,
                default_output_path=metadata.default_output_path,
                legacy_output_path=metadata.legacy_output_path,
            ),
        )

    return tuple(registry)


@lru_cache(maxsize=1)
def get_wiki_seed_registry() -> tuple[SeedRegistryEntry, ...]:
    return build_discovered_layer_one_seed_registry()


def validate_unique_seed_name(
    *,
    seed_name: str,
    seen_seed_names: set[str],
    duplicate_message: Callable[[str], str],
) -> None:
    if seed_name in seen_seed_names:
        msg = duplicate_message(seed_name)
        raise ValueError(msg)
    seen_seed_names.add(seed_name)


def validate_wikipedia_url(
    *,
    seed_name: str,
    wikipedia_url: str,
    message: Callable[[str], str],
) -> None:
    if not wikipedia_url.strip():
        msg = message(seed_name)
        raise ValueError(msg)


def validate_path_prefix(
    *,
    entry: BaseRegistryEntry,
    rule: RegistryValidationRule,
) -> None:
    output_path = rule.extractor(entry)
    prefix = rule.expected_prefix(entry)
    if not output_path.startswith(prefix):
        msg = rule.message(entry)
        raise ValueError(msg)


def validate_registry(
    *,
    registry: tuple[BaseRegistryEntry, ...],
    spec: RegistryValidationSpec,
) -> None:
    seen_seed_names: set[str] = set()

    for entry in registry:
        validate_registry_entry(
            entry=entry,
            spec=spec,
            seen_seed_names=seen_seed_names,
        )


def validate_seed_registry(
    registry: tuple[SeedRegistryEntry, ...] | None = None,
) -> None:
    if registry is None:
        registry = get_wiki_seed_registry()
    validate_registry(registry=registry, spec=SEED_REGISTRY_VALIDATION_SPEC)


def validate_list_job_registry(
    registry: tuple[ListJobRegistryEntry, ...] = WIKI_LIST_JOB_REGISTRY,
) -> None:
    validate_registry(registry=registry, spec=LIST_JOB_REGISTRY_VALIDATION_SPEC)

def resolve_wikipedia_url(list_scraper_cls: type[Any]) -> str:
    config = getattr(list_scraper_cls, "CONFIG", None)
    if config is not None and hasattr(config, "url"):
        return config.url

    url = getattr(list_scraper_cls, "url", None)
    if isinstance(url, str):
        return url

    msg = f"Cannot resolve wikipedia_url for scraper '{list_scraper_cls.__name__}'"
    raise ValueError(msg)


def seed_default_output_path(*, output_category: str, filename: str) -> str:
    return f"raw/{output_category}/seeds/{filename}"


def seed_legacy_output_path(*, output_category: str, filename: str) -> str:
    return f"{output_category}/{filename}"


def list_default_output_path(*, output_category: str, filename: str) -> str:
    return f"raw/{output_category}/list/{filename}"


def list_legacy_output_path(*, output_category: str, filename: str) -> str:
    return f"{output_category}/{filename}"


def build_seed_registry_entry_from_spec(
    spec: RawRegistrySpec,
) -> SeedRegistryEntry | None:
    if spec.seed_filename is None:
        return None

    output_category = spec.seed_output_category or spec.output_category
    return SeedRegistryEntry(
        seed_name=spec.seed_name,
        wikipedia_url=resolve_wikipedia_url(spec.list_scraper_cls),
        output_category=output_category,
        list_scraper_cls=spec.list_scraper_cls,
        default_output_path=seed_default_output_path(
            output_category=output_category,
            filename=spec.seed_filename,
        ),
        legacy_output_path=seed_legacy_output_path(
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
        wikipedia_url=resolve_wikipedia_url(spec.list_scraper_cls),
        output_category=output_category,
        list_scraper_cls=spec.list_scraper_cls,
        json_output_path=list_default_output_path(
            output_category=output_category,
            filename=spec.list_filename,
        ),
        legacy_json_output_path=list_legacy_output_path(
            output_category=output_category,
            filename=spec.list_filename,
        ),
    )

def validate_seed_name_consistency_at_startup() -> None:
    validate_sources_registry_consistency()

    resolved_seed_names: set[str] = set()
    for configured_seed_name in LIST_SCRAPER_BY_SEED_NAME:
        canonical_seed_name = resolve_seed_name(configured_seed_name, warn=False)
        get_source_by_seed_name(canonical_seed_name, warn=False)
        if canonical_seed_name in resolved_seed_names:
            msg = (
                "Duplicate canonical seed_name in _LIST_SCRAPER_BY_SEED_NAME "
                f"after legacy alias resolution: {canonical_seed_name!r}"
            )
            raise ValueError(msg)
        resolved_seed_names.add(canonical_seed_name)

    for configured_seed_name in SEED_FILENAME_OVERRIDES:
        get_source_by_seed_name(configured_seed_name, warn=False)


def build_raw_registry_spec() -> tuple[RawRegistrySpec, ...]:
    validate_seed_name_consistency_at_startup()

    specs: list[RawRegistrySpec] = []
    for seed_name, list_scraper_cls in LIST_SCRAPER_BY_SEED_NAME.items():
        source = get_source_by_seed_name(seed_name, warn=False)
        specs.append(
            RawRegistrySpec(
                seed_name=source.seed_name,
                list_scraper_cls=list_scraper_cls,
                output_category=source.domain,
                list_filename=source.output_file,
                seed_filename=SEED_FILENAME_OVERRIDES.get(source.seed_name),
            ),
        )

    constructors_source = get_source_by_seed_name("constructors", warn=False)
    specs.append(
        RawRegistrySpec(
            seed_name="constructors",
            list_scraper_cls=ConstructorsListScraper,
            output_category=constructors_source.domain,
            list_filename=constructors_source.output_file,
            seed_filename=SEED_FILENAME_OVERRIDES["constructors"],
            include_in_list_registry=False,
        ),
    )

    grands_prix_source = get_source_by_seed_name("grands_prix", warn=False)
    specs.append(
        RawRegistrySpec(
            seed_name="grands_prix",
            list_scraper_cls=GrandsPrixListScraper,
            output_category=grands_prix_source.domain,
            list_filename=grands_prix_source.output_file,
            seed_filename=SEED_FILENAME_OVERRIDES["grands_prix"],
            include_in_list_registry=False,
        ),
    )
    return tuple(specs)

def validate_registry_startup_consistency() -> None:
    for spec in RAW_REGISTRY_SPEC:
        source = get_source_by_seed_name(spec.seed_name, warn=False)
        if spec.output_category != source.domain:
            msg = (
                "Seed registry startup consistency check failed for output_category: "
                f"{spec.seed_name!r} -> {spec.output_category!r} "
                f"(expected {source.domain!r})"
            )
            raise ValueError(msg)
        if spec.list_filename != source.output_file:
            msg = (
                "Seed registry startup consistency check failed for list_filename: "
                f"{spec.seed_name!r} -> {spec.list_filename!r} "
                f"(expected {source.output_file!r})"
            )
            raise ValueError(msg)
