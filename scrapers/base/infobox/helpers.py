"""DEPRECATED: use `scrapers.base.infobox.infobox_parsing` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from scrapers.base.infobox.infobox_parsing import (
    parse_infobox_from_soup,
)


__all__ = [
    'parse_infobox_from_soup',
]
