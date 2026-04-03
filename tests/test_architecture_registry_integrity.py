from __future__ import annotations

from pathlib import Path

from tests.architecture.registry import ARCHITECTURE_REGISTRY

IGNORED_PACKAGES = {"base", "wiki", "__pycache__"}


def test_registry_domains_are_complete_against_scrapers_packages() -> None:
    discovered_domains = {
        path.name
        for path in Path("scrapers").iterdir()
        if path.is_dir() and path.name not in IGNORED_PACKAGES
    }
    assert discovered_domains == set(ARCHITECTURE_REGISTRY.domain_names)


def test_registry_entrypoint_domains_match_filesystem() -> None:
    discovered_entrypoints = {
        path.name
        for path in Path("scrapers").iterdir()
        if path.is_dir() and (path / "entrypoint.py").exists()
    }
    assert discovered_entrypoints == set(ARCHITECTURE_REGISTRY.entrypoint_domains)


def test_registry_layer_dependency_maps_are_consistent() -> None:
    layers = set(ARCHITECTURE_REGISTRY.layers)
    assert set(ARCHITECTURE_REGISTRY.forbidden_imports_by_layer) == layers
    assert set(ARCHITECTURE_REGISTRY.allowed_imports_by_layer) == layers

    for layer in ARCHITECTURE_REGISTRY.layers:
        forbidden = set(ARCHITECTURE_REGISTRY.forbidden_imports_by_layer[layer])
        allowed = set(ARCHITECTURE_REGISTRY.allowed_imports_by_layer[layer])

        assert layer not in forbidden
        assert allowed <= layers
        assert forbidden.isdisjoint(allowed)
        assert allowed | {layer} == layers - (forbidden & layers)

        extra_forbidden = forbidden - layers
        assert extra_forbidden <= {"single_scraper"}


def test_registry_required_layers_are_valid_and_scoped_to_entrypoints() -> None:
    layers = set(ARCHITECTURE_REGISTRY.layers)
    entrypoint_domains = set(ARCHITECTURE_REGISTRY.entrypoint_domains)

    assert set(ARCHITECTURE_REGISTRY.required_layers_by_domain) == entrypoint_domains

    for (
        domain,
        required_layers,
    ) in ARCHITECTURE_REGISTRY.required_layers_by_domain.items():
        assert required_layers, f"Entrypoint domain without required layers: {domain}"
        assert set(required_layers) <= layers
