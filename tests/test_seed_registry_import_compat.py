import importlib


def test_seed_registry_import_paths_are_compatible() -> None:
    canonical = importlib.import_module("layers.seed.registry")
    facade = importlib.import_module("scrapers.wiki.seed_registry")

    symbols = (
        "SeedRegistryEntry",
        "ListJobRegistryEntry",
        "WIKI_LIST_JOB_REGISTRY",
        "WIKI_SEED_REGISTRY",
        "get_wiki_seed_registry",
        "validate_seed_registry",
        "validate_list_job_registry",
        "clear_wiki_seed_registry_cache",
    )

    for symbol in symbols:
        assert getattr(facade, symbol) is getattr(canonical, symbol)
