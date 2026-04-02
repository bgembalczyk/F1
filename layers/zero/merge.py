"""Transitional compatibility module for Layer 0 merge.

Deprecated: use `layers.zero.merge_orchestrator` and role-specific modules:
- `layers.zero.merge_transformations`
- `layers.zero.merge_post_process`
- `layers.zero.merge_io`
"""

from __future__ import annotations

import warnings
from pathlib import Path

from layers.zero.merge_orchestrator import merge_layer_zero_raw_outputs as _merge_orchestrator
from layers.zero.merge_transformations import _circuits_domain_handler
from layers.zero.merge_transformations import _constructor_domain_handler
from layers.zero.merge_transformations import _drivers_domain_handler
from layers.zero.merge_transformations import _engines_domain_handler
from layers.zero.merge_transformations import _grands_prix_domain_handler
from layers.zero.merge_transformations import _races_domain_handler
from layers.zero.merge_transformations import _resolve_record_transform_handlers
from layers.zero.merge_transformations import _teams_domain_handler
from layers.zero.merge_transformations import _tyre_manufacturers_handler

_DEPRECATION_MESSAGE = (
    "layers.zero.merge is deprecated and will be removed in a future release; "
    "use layers.zero.merge_orchestrator instead."
)


def _warn_deprecated_module() -> None:
    warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)


def merge_layer_zero_raw_outputs(base_wiki_dir: Path) -> None:
    _warn_deprecated_module()
    _merge_orchestrator(base_wiki_dir)
