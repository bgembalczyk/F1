"""Public API for layer orchestration.

The package exposes selected factories and runner helpers while keeping imports
lazy to avoid circular bootstrap dependencies.
"""

from __future__ import annotations

from importlib import import_module

__all__ = [
    "DefaultLayerZeroRunConfigFactory",
    "LayerZeroRunConfigFactory",
    "SponsorshipLiveriesRunConfigFactory",
    "StaticScraperKwargsFactory",
    "build_layer_one_runner_map",
    "build_layer_zero_run_config_factory_map",
    "run_engine_manufacturers",
]

from layers.orchestration.factories import DefaultLayerZeroRunConfigFactory
from layers.orchestration.factories import LayerZeroRunConfigFactory
from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
from layers.orchestration.factories import StaticScraperKwargsFactory
from layers.orchestration.runner_registry import build_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map
from layers.orchestration.runner_registry import run_engine_manufacturers


def __getattr__(name: str) -> object:
    if name in {
        "DefaultLayerZeroRunConfigFactory",
        "LayerZeroRunConfigFactory",
        "SponsorshipLiveriesRunConfigFactory",
        "StaticScraperKwargsFactory",
    }:
        module = import_module("layers.orchestration.factories")
        return getattr(module, name)

    if name in {
        "build_layer_one_runner_map",
        "build_layer_zero_run_config_factory_map",
        "run_engine_manufacturers",
    }:
        module = import_module("layers.orchestration.runner_registry")
        return getattr(module, name)

    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
