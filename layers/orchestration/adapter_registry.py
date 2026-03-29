from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from importlib import import_module
from typing import TYPE_CHECKING
from typing import Protocol
from typing import runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Callable

    from layers.seed.registry.entries import ListJobRegistryEntry
    from layers.seed.registry.entries import SeedRegistryEntry


@runtime_checkable
class LayerZeroConfigFactoryContract(Protocol):
    def create_scraper_kwargs(
        self,
        _job: ListJobRegistryEntry,
    ) -> dict[str, object]: ...


@runtime_checkable
class LayerJobRunnerContract(Protocol):
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: object,
        base_wiki_dir: object,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class LayerZeroAdapterSet:
    list_job_registry: tuple[ListJobRegistryEntry, ...]
    validate_list_registry: Callable[[tuple[ListJobRegistryEntry, ...]], None]
    run_config_factory_map_builder: Callable[
        [],
        dict[str, LayerZeroConfigFactoryContract],
    ]
    default_config_factory: LayerZeroConfigFactoryContract
    run_and_export_function: Callable[..., None]


@dataclass(frozen=True, slots=True)
class LayerOneAdapterSet:
    seed_registry: tuple[SeedRegistryEntry, ...]
    validate_seed_registry_function: Callable[[tuple[SeedRegistryEntry, ...]], None]
    runner_map_builder: Callable[[], dict[str, LayerJobRunnerContract]]
    engine_manufacturers_runner: Callable[..., None]


@dataclass(frozen=True, slots=True)
class LayerAdapterRegistry:
    layer_zero: LayerZeroAdapterSet
    layer_one: LayerOneAdapterSet


def _import_target(path: str) -> object:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, attr_name)


@cache
def get_default_layer_adapter_registry() -> LayerAdapterRegistry:
    default_l0_factory = _import_target(
        "layers.orchestration.factories:DefaultLayerZeroRunConfigFactory",
    )
    return LayerAdapterRegistry(
        layer_zero=LayerZeroAdapterSet(
            list_job_registry=_import_target(
                "layers.seed.registry.constants:WIKI_LIST_JOB_REGISTRY",
            ),
            validate_list_registry=_import_target(
                "layers.seed.registry.helpers:validate_list_job_registry",
            ),
            run_config_factory_map_builder=_import_target(
                "layers.orchestration.helpers:build_layer_zero_run_config_factory_map",
            ),
            default_config_factory=default_l0_factory(),
            run_and_export_function=_import_target(
                "scrapers.base.helpers.runner:run_and_export",
            ),
        ),
        layer_one=LayerOneAdapterSet(
            seed_registry=_import_target(
                "layers.seed.registry.helpers:WIKI_SEED_REGISTRY",
            ),
            validate_seed_registry_function=_import_target(
                "layers.seed.registry.helpers:validate_seed_registry",
            ),
            runner_map_builder=_import_target(
                "layers.orchestration.helpers:build_layer_one_runner_map",
            ),
            engine_manufacturers_runner=_import_target(
                "layers.orchestration.helpers:run_engine_manufacturers",
            ),
        ),
    )


def _validate_layer_zero_adapter_set(layer_zero: LayerZeroAdapterSet) -> None:
    if not isinstance(layer_zero.list_job_registry, tuple):
        msg = "Layer zero registry must be a tuple."
        raise TypeError(msg)
    if not callable(layer_zero.validate_list_registry):
        msg = "Layer zero validate_list_registry must be callable."
        raise TypeError(msg)
    if not isinstance(
        layer_zero.default_config_factory,
        LayerZeroConfigFactoryContract,
    ):
        msg = "Layer zero default config factory violates contract."
        raise TypeError(msg)

    l0_factories = layer_zero.run_config_factory_map_builder()
    if not isinstance(l0_factories, dict):
        msg = "Layer zero config factory map builder must return dict."
        raise TypeError(msg)

    known_seeds = {job.seed_name for job in layer_zero.list_job_registry}
    for seed_name, factory in l0_factories.items():
        if not isinstance(seed_name, str):
            msg = "Layer zero config factory key must be str."
            raise TypeError(msg)
        if seed_name not in known_seeds:
            msg = f"Layer zero config factory map references unknown seed: {seed_name}"
            raise ValueError(msg)
        if not isinstance(factory, LayerZeroConfigFactoryContract):
            msg = f"Layer zero config factory for {seed_name!r} violates contract."
            raise TypeError(msg)


def _validate_layer_one_adapter_set(layer_one: LayerOneAdapterSet) -> None:
    if not isinstance(layer_one.seed_registry, tuple):
        msg = "Layer one registry must be a tuple."
        raise TypeError(msg)
    if not callable(layer_one.validate_seed_registry_function):
        msg = "Layer one validate_seed_registry_function must be callable."
        raise TypeError(msg)

    l1_runners = layer_one.runner_map_builder()
    if not isinstance(l1_runners, dict):
        msg = "Layer one runner map builder must return dict."
        raise TypeError(msg)

    known_seeds = {seed.seed_name for seed in layer_one.seed_registry}
    for seed_name, runner in l1_runners.items():
        if not isinstance(seed_name, str):
            msg = "Layer one runner map key must be str."
            raise TypeError(msg)
        if seed_name not in known_seeds:
            msg = f"Layer one runner map references unknown seed: {seed_name}"
            raise ValueError(msg)
        if not isinstance(runner, LayerJobRunnerContract):
            msg = f"Layer one runner for {seed_name!r} violates contract."
            raise TypeError(msg)

    if not callable(layer_one.engine_manufacturers_runner):
        msg = "Layer one engine_manufacturers_runner must be callable."
        raise TypeError(msg)


def validate_layer_adapter_registry(registry: LayerAdapterRegistry) -> None:
    _validate_layer_zero_adapter_set(registry.layer_zero)
    _validate_layer_one_adapter_set(registry.layer_one)
