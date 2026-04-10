from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from typing import Any
from warnings import warn

CREATE_DEPRECATION_MESSAGE = (
    "RecordFactory.create(payload) is deprecated; use build(record) instead."
)


def create_compat(
    payload: Mapping[str, Any],
    builder: Callable[[Mapping[str, Any]], Any],
) -> Any:
    """Compatibility adapter for legacy ``create(payload)`` entrypoints."""
    warn(CREATE_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
    return builder(payload)


__all__ = ["CREATE_DEPRECATION_MESSAGE", "create_compat"]
