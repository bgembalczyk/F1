"""DEPRECATED: use `models.records.factories.field_normalization` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from models.records.factories.field_normalization import (
    normalize_points,
    normalize_optional_link_or_string,
    normalize_optional_link_list_or_link_or_string,
)


__all__ = [
    'normalize_points', 'normalize_optional_link_or_string', 'normalize_optional_link_list_or_link_or_string',
]
