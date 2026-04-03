"""Compatibility facade for legacy imports.

Canonical source: ``layers.seed.registry``.
"""

from layers.seed.registry import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry import ListJobRegistryEntry
from layers.seed.registry import SeedRegistryEntry
from layers.seed.registry import clear_wiki_seed_registry_cache
from layers.seed.registry import get_wiki_seed_registry
from layers.seed.registry import validate_list_job_registry
from layers.seed.registry import validate_seed_registry

WIKI_SEED_REGISTRY = get_wiki_seed_registry()

__all__ = [
    "ListJobRegistryEntry",
    "SeedRegistryEntry",
    "WIKI_LIST_JOB_REGISTRY",
    "WIKI_SEED_REGISTRY",
    "clear_wiki_seed_registry_cache",
    "get_wiki_seed_registry",
    "validate_list_job_registry",
    "validate_seed_registry",
]
