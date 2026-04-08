import warnings

from layers.orchestration.runner_registry import build_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map

warnings.warn(
    "Moduł layers.orchestration.helpers jest przestarzały — użyj "
    "layers.orchestration.runner_registry.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "build_layer_one_runner_map",
    "build_layer_zero_run_config_factory_map",
]
