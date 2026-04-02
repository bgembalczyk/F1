"""Legacy alias for layer-zero path/run-profile helpers.

Prefer importing from ``layers.zero.run_profile_paths``.
"""

from __future__ import annotations

import warnings

from layers.zero.run_profile_paths import LayerZeroPathBuilder
from layers.zero.run_profile_paths import build_debug_run_config
from layers.zero.run_profile_paths import layer_zero_raw_paths

warnings.warn(
    "layers.zero.helpers is deprecated; use layers.zero.run_profile_paths instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["LayerZeroPathBuilder", "build_debug_run_config", "layer_zero_raw_paths"]
