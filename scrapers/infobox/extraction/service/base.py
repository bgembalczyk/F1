from __future__ import annotations

from warnings import warn

from .base_orchestrator import BaseInfoboxOrchestrator

warn(
    "scrapers.infobox.extraction.service.base is deprecated; use "
    "scrapers.infobox.extraction.service.base_orchestrator",
    DeprecationWarning,
    stacklevel=2,
)

BaseInfoboxExtractionService = BaseInfoboxOrchestrator

__all__ = ["BaseInfoboxExtractionService", "BaseInfoboxOrchestrator"]
