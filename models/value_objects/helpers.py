"""DEPRECATED: use `models.value_objects.text_normalization` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from models.value_objects.text_normalization import (
    normalize_iso,
    normalize_text,
)


__all__ = [
    'normalize_iso', 'normalize_text',
]
