"""Canonical API dla registry seedów wiki (single source of truth)."""

from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from layers.seed.registry.helpers import clear_wiki_seed_registry_cache
from layers.seed.registry.helpers import get_wiki_seed_registry
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry

# Backward-compatible alias for callers expecting eager tuple constant.
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
