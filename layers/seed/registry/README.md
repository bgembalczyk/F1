# layers/seed/registry

Pakiet utrzymuje rejestr seedów wiki i jego walidację.

## Public API
- `layers.seed.registry.WIKI_LIST_JOB_REGISTRY`
- `layers.seed.registry.WIKI_SEED_REGISTRY`
- `layers.seed.registry.get_wiki_seed_registry`
- `layers.seed.registry.validate_seed_registry`
- `layers.seed.registry.validate_list_job_registry`
- `layers.seed.registry.clear_wiki_seed_registry_cache`
- `layers.seed.registry.SeedRegistryEntry`
- `layers.seed.registry.ListJobRegistryEntry`

## Internal
`constants.py`, `entries.py` i `helpers.py` są modułami internal; konsumenci powinni importować wyłącznie przez `layers.seed.registry`.
