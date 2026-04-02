"""Legacy alias for orchestration runner registry.

Prefer importing from ``layers.orchestration.runner_registry``.
"""

from __future__ import annotations

import warnings

from layers.orchestration.runner_registry import _build_explicit_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map
from layers.orchestration.runner_registry import run_engine_manufacturers

warnings.warn(
    "layers.orchestration.helpers is deprecated; "
    "use layers.orchestration.runner_registry instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "_build_explicit_layer_one_runner_map",
    "build_layer_one_runner_map",
    "build_layer_zero_run_config_factory_map",
    "run_engine_manufacturers",
]
