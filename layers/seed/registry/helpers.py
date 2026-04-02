"""DEPRECATED: use `layers.seed.registry.registry_validation` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from layers.seed.registry.registry_validation import (
    _seed_entry_from_component,
    _validate_registry_entry,
    _build_discovered_layer_one_seed_registry,
    get_wiki_seed_registry,
    clear_wiki_seed_registry_cache,
    _validate_unique_seed_name,
    _validate_wikipedia_url,
    _validate_path_prefix,
    _validate_registry,
    validate_seed_registry,
    validate_list_job_registry,
)


__all__ = [
    '_seed_entry_from_component', '_validate_registry_entry', '_build_discovered_layer_one_seed_registry', 'get_wiki_seed_registry', 'clear_wiki_seed_registry_cache', '_validate_unique_seed_name', '_validate_wikipedia_url', '_validate_path_prefix', '_validate_registry', 'validate_seed_registry', 'validate_list_job_registry',
]
