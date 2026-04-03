from collections.abc import Callable
from functools import lru_cache
from typing import Any

from layers.seed.data_classes import RegistryValidationRule
from layers.seed.data_classes import RegistryValidationSpec
from layers.seed.registry.constants import EXPLICIT_LAYER_ONE_SEED_REGISTRY
from layers.seed.registry.constants import LIST_JOB_REGISTRY_VALIDATION_SPEC
from layers.seed.registry.constants import SEED_REGISTRY_VALIDATION_SPEC
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.entries import BaseRegistryEntry
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
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
    entry: BaseRegistryEntry,
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
            _seed_entry_from_component(
                seed_name=seed_name,
                component=component,
                default_output_path=metadata.default_output_path,
                legacy_output_path=metadata.legacy_output_path,
            ),
        )

    return tuple(registry)


@lru_cache(maxsize=1)
def get_wiki_seed_registry() -> tuple[SeedRegistryEntry, ...]:
    return _build_discovered_layer_one_seed_registry()


def clear_wiki_seed_registry_cache() -> None:
    get_wiki_seed_registry.cache_clear()


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


def _validate_path_prefix(
    *,
    entry: BaseRegistryEntry,
    rule: RegistryValidationRule,
) -> None:
    output_path = rule.extractor(entry)
    prefix = rule.expected_prefix(entry)
    if not output_path.startswith(prefix):
        msg = rule.message(entry)
        raise ValueError(msg)


def _validate_registry(
    *,
    registry: tuple[BaseRegistryEntry, ...],
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
    registry: tuple[SeedRegistryEntry, ...] | None = None,
) -> None:
    if registry is None:
        registry = get_wiki_seed_registry()
    _validate_registry(registry=registry, spec=SEED_REGISTRY_VALIDATION_SPEC)


def validate_list_job_registry(
    registry: tuple[ListJobRegistryEntry, ...] = WIKI_LIST_JOB_REGISTRY,
) -> None:
    _validate_registry(registry=registry, spec=LIST_JOB_REGISTRY_VALIDATION_SPEC)
