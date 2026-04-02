"""DEPRECATED: use `scrapers.base.parsers.record_parsing` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from scrapers.base.parsers.record_parsing import (
    EntriesStarts,
    NumericValue,
    extract_visible_text,
    parse_entries_starts,
    normalize_unit,
    parse_unit_list,
    extract_driver_text,
)


__all__ = [
    'EntriesStarts', 'NumericValue', 'extract_visible_text', 'parse_entries_starts', 'normalize_unit', 'parse_unit_list', 'extract_driver_text',
]
