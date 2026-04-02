"""DEPRECATED: use `scrapers.seasons.season_export` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from scrapers.seasons.season_export import (
    season_filename,
    export_complete_seasons,
)


__all__ = [
    'season_filename', 'export_complete_seasons',
]
