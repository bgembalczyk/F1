"""DEPRECATED: use `layers.zero.run_paths` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from layers.zero.run_paths import (
    LayerZeroPathBuilder,
    build_debug_run_config,
    layer_zero_raw_paths,
)


__all__ = [
    'LayerZeroPathBuilder', 'build_debug_run_config', 'layer_zero_raw_paths',
]
