from __future__ import annotations

import pytest

from layers.orchestration.adapter_registry import LayerAdapterRegistry
from layers.orchestration.adapter_registry import LayerOneAdapterSet
from layers.orchestration.adapter_registry import LayerZeroAdapterSet
from layers.orchestration.adapter_registry import get_default_layer_adapter_registry
from layers.orchestration.adapter_registry import validate_layer_adapter_registry
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry


class _FakeScraper:
    pass


class _Factory:
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        return {}


class _Runner:
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: object,
        base_wiki_dir: object,
    ) -> None:
        _ = (seed, run_config, base_wiki_dir)


def _noop(*_args: object, **_kwargs: object) -> None:
    return None


def _build_registry_with_seed(seed_name: str = "drivers") -> LayerAdapterRegistry:
    list_entry = ListJobRegistryEntry(
        seed_name=seed_name,
        wikipedia_url="https://example.com/list",
        output_category=seed_name,
        list_scraper_cls=_FakeScraper,
        json_output_path=f"{seed_name}/out.json",
        legacy_json_output_path=f"{seed_name}/legacy.json",
    )
    seed_entry = SeedRegistryEntry(
        seed_name=seed_name,
        wikipedia_url="https://example.com/seed",
        output_category=seed_name,
        list_scraper_cls=_FakeScraper,
        default_output_path=f"{seed_name}/default.json",
        legacy_output_path=f"{seed_name}/legacy.json",
    )
    return LayerAdapterRegistry(
        layer_zero=LayerZeroAdapterSet(
            list_job_registry=(list_entry,),
            validate_list_registry=lambda _registry: None,
            run_config_factory_map_builder=lambda: {seed_name: _Factory()},
            default_config_factory=_Factory(),
            run_and_export_function=_noop,
        ),
        layer_one=LayerOneAdapterSet(
            seed_registry=(seed_entry,),
            validate_seed_registry_function=lambda _registry: None,
            runner_map_builder=lambda: {seed_name: _Runner()},
            engine_manufacturers_runner=_noop,
        ),
    )


def test_default_registry_passes_runtime_validation() -> None:
    registry = get_default_layer_adapter_registry()

    validate_layer_adapter_registry(registry)


def test_runtime_validation_rejects_unknown_seed_in_layer_zero_factories() -> None:
    registry = _build_registry_with_seed(seed_name="drivers")
    broken_registry = LayerAdapterRegistry(
        layer_zero=LayerZeroAdapterSet(
            list_job_registry=registry.layer_zero.list_job_registry,
            validate_list_registry=registry.layer_zero.validate_list_registry,
            run_config_factory_map_builder=lambda: {"unknown": _Factory()},
            default_config_factory=registry.layer_zero.default_config_factory,
            run_and_export_function=registry.layer_zero.run_and_export_function,
        ),
        layer_one=registry.layer_one,
    )

    with pytest.raises(ValueError, match="unknown seed"):
        validate_layer_adapter_registry(broken_registry)


def test_runtime_validation_rejects_unknown_seed_in_layer_one_runners() -> None:
    registry = _build_registry_with_seed(seed_name="drivers")
    broken_registry = LayerAdapterRegistry(
        layer_zero=registry.layer_zero,
        layer_one=LayerOneAdapterSet(
            seed_registry=registry.layer_one.seed_registry,
            validate_seed_registry_function=(
                registry.layer_one.validate_seed_registry_function
            ),
            runner_map_builder=lambda: {"unknown": _Runner()},
            engine_manufacturers_runner=registry.layer_one.engine_manufacturers_runner,
        ),
    )

    with pytest.raises(ValueError, match="unknown seed"):
        validate_layer_adapter_registry(broken_registry)
