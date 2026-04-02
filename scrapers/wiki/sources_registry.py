from __future__ import annotations

import warnings
from dataclasses import dataclass

from scrapers.wiki.pipeline_spec import LEGACY_LIST_FILENAME_ALIASES
from scrapers.wiki.pipeline_spec import LEGACY_SEED_NAME_ALIASES
from scrapers.wiki.pipeline_spec import iter_source_specs
from scrapers.wiki.pipeline_spec import validate_wiki_pipeline_spec


@dataclass(frozen=True)
class WikiSourceDefinition:
    seed_name: str
    output_category: str
    list_filename: str


WIKI_SOURCE_DEFINITIONS: tuple[WikiSourceDefinition, ...] = tuple(
    WikiSourceDefinition(
        seed_name=seed_name,
        output_category=domain,
        list_filename=list_filename,
    )
    for seed_name, domain, list_filename in iter_source_specs()
)

SOURCE_BY_SEED_NAME: dict[str, WikiSourceDefinition] = {
    source.seed_name: source for source in WIKI_SOURCE_DEFINITIONS
}
SOURCE_BY_LIST_FILENAME: dict[str, WikiSourceDefinition] = {
    source.list_filename: source for source in WIKI_SOURCE_DEFINITIONS
}

ENGINES_INDIANAPOLIS_ONLY_LEGACY_SOURCE = (
    "f1_engine_manufacturers_indianapolis_only.json"
)

FORMER_CONSTRUCTORS_SOURCE = SOURCE_BY_SEED_NAME["constructors_former"].list_filename
INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE = SOURCE_BY_SEED_NAME[
    "constructors_indianapolis_only"
].list_filename
TYRE_MANUFACTURERS_SOURCE = SOURCE_BY_SEED_NAME["tyres"].list_filename


def _emit_deprecation_warning(kind: str, legacy: str, canonical: str) -> None:
    warnings.warn(
        (
            f"Legacy {kind} alias '{legacy}' is deprecated and will be removed in a future release; "
            f"use canonical value '{canonical}'."
        ),
        DeprecationWarning,
        stacklevel=3,
    )


def resolve_seed_name(seed_name: str, *, warn: bool = True) -> str:
    canonical = LEGACY_SEED_NAME_ALIASES.get(seed_name, seed_name)
    if canonical != seed_name and warn:
        _emit_deprecation_warning("seed_name", seed_name, canonical)
    return canonical


def resolve_list_filename(list_filename: str, *, warn: bool = True) -> str:
    canonical = LEGACY_LIST_FILENAME_ALIASES.get(list_filename, list_filename)
    if canonical != list_filename and warn:
        _emit_deprecation_warning("list filename", list_filename, canonical)
    return canonical


def get_source_by_seed_name(seed_name: str, *, warn: bool = True) -> WikiSourceDefinition:
    canonical_seed_name = resolve_seed_name(seed_name, warn=warn)
    try:
        return SOURCE_BY_SEED_NAME[canonical_seed_name]
    except KeyError as exc:
        msg = f"Unknown wiki source seed_name: {seed_name!r}"
        raise KeyError(msg) from exc


def get_source_by_list_filename(
    list_filename: str,
    *,
    warn: bool = True,
) -> WikiSourceDefinition:
    canonical_list_filename = resolve_list_filename(list_filename, warn=warn)
    try:
        return SOURCE_BY_LIST_FILENAME[canonical_list_filename]
    except KeyError as exc:
        msg = f"Unknown wiki source list filename: {list_filename!r}"
        raise KeyError(msg) from exc


def validate_sources_registry_consistency() -> None:
    validate_wiki_pipeline_spec()
    seen_seed_names: set[str] = set()
    seen_filenames: set[str] = set()

    for source in WIKI_SOURCE_DEFINITIONS:
        if source.seed_name in seen_seed_names:
            msg = f"Duplicate canonical seed_name in wiki sources registry: {source.seed_name}"
            raise ValueError(msg)
        seen_seed_names.add(source.seed_name)

        if source.list_filename in seen_filenames:
            msg = (
                "Duplicate canonical list_filename in wiki sources registry: "
                f"{source.list_filename}"
            )
            raise ValueError(msg)
        seen_filenames.add(source.list_filename)

    for legacy_seed_name, canonical_seed_name in LEGACY_SEED_NAME_ALIASES.items():
        if canonical_seed_name not in SOURCE_BY_SEED_NAME:
            msg = (
                "Legacy seed alias points to missing canonical seed: "
                f"{legacy_seed_name} -> {canonical_seed_name}"
            )
            raise ValueError(msg)

    for legacy_filename, canonical_filename in LEGACY_LIST_FILENAME_ALIASES.items():
        if canonical_filename not in SOURCE_BY_LIST_FILENAME:
            msg = (
                "Legacy filename alias points to missing canonical list filename: "
                f"{legacy_filename} -> {canonical_filename}"
            )
            raise ValueError(msg)


validate_sources_registry_consistency()


__all__ = [
    "FORMER_CONSTRUCTORS_SOURCE",
    "ENGINES_INDIANAPOLIS_ONLY_LEGACY_SOURCE",
    "INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE",
    "LEGACY_LIST_FILENAME_ALIASES",
    "LEGACY_SEED_NAME_ALIASES",
    "SOURCE_BY_LIST_FILENAME",
    "SOURCE_BY_SEED_NAME",
    "TYRE_MANUFACTURERS_SOURCE",
    "WIKI_SOURCE_DEFINITIONS",
    "WikiSourceDefinition",
    "get_source_by_list_filename",
    "get_source_by_seed_name",
    "resolve_list_filename",
    "resolve_seed_name",
    "validate_sources_registry_consistency",
]
