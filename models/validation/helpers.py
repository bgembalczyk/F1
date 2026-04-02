"""DEPRECATED: use `models.validation.value_validation` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from models.validation.value_validation import (
    validate_int,
    validate_float,
    validate_status,
    normalize_unit_value,
    normalize_unit_list,
    normalize_range_value,
    normalize_range_item,
)


__all__ = [
    'validate_int', 'validate_float', 'validate_status', 'normalize_unit_value', 'normalize_unit_list', 'normalize_range_value', 'normalize_range_item',
]
