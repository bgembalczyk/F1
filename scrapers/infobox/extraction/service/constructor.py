from __future__ import annotations

from warnings import warn

from .constructor_orchestrator import ConstructorInfoboxOrchestrator

warn(
    "scrapers.infobox.extraction.service.constructor is deprecated; use "
    "scrapers.infobox.extraction.service.constructor_orchestrator",
    DeprecationWarning,
    stacklevel=2,
)

ConstructorInfoboxExtractionService = ConstructorInfoboxOrchestrator

__all__ = ["ConstructorInfoboxExtractionService", "ConstructorInfoboxOrchestrator"]
