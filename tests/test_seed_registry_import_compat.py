import importlib


def test_seed_registry_import_paths_are_compatible() -> None:
    canonical = importlib.import_module("layers.seed.registry")
    canonical.get_wiki_seed_registry.cache_clear()
    facade = importlib.import_module("scrapers.wiki.seed_registry")

    symbols = (
        "SeedRegistryEntry",
        "ListJobRegistryEntry",
        "WIKI_LIST_JOB_REGISTRY",
        "WIKI_SEED_REGISTRY",
        "get_wiki_seed_registry",
        "validate_seed_registry",
        "validate_list_job_registry",
    )

    for symbol in symbols:
        facade_symbol = getattr(facade, symbol)
        canonical_symbol = getattr(canonical, symbol)
        if symbol == "WIKI_SEED_REGISTRY":
            assert facade_symbol == canonical_symbol
            continue
        assert facade_symbol is canonical_symbol
