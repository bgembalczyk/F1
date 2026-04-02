"""DEPRECATED: use `layers.seed.record_extraction` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from layers.seed.record_extraction import (
    _extract_name,
    _extract_link,
    _coerce_text,
    _coerce_link,
)


__all__ = [
    '_extract_name', '_extract_link', '_coerce_text', '_coerce_link',
]
