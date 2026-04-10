from __future__ import annotations

from warnings import warn

from .driver_orchestrator import DriverInfoboxOrchestrator

warn(
    "scrapers.infobox.extraction.service.driver is deprecated; use "
    "scrapers.infobox.extraction.service.driver_orchestrator",
    DeprecationWarning,
    stacklevel=2,
)

DriverInfoboxExtractionService = DriverInfoboxOrchestrator

__all__ = ["DriverInfoboxExtractionService", "DriverInfoboxOrchestrator"]
