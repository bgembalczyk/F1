from __future__ import annotations

from warnings import warn

from .circuit_orchestrator import CircuitInfoboxOrchestrator

warn(
    "scrapers.infobox.extraction.service.circuit is deprecated; use "
    "scrapers.infobox.extraction.service.circuit_orchestrator",
    DeprecationWarning,
    stacklevel=2,
)

CircuitInfoboxExtractionService = CircuitInfoboxOrchestrator

__all__ = ["CircuitInfoboxExtractionService", "CircuitInfoboxOrchestrator"]
