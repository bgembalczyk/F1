from __future__ import annotations

from warnings import warn

from .strategy_orchestrator import StrategyBackedInfoboxOrchestrator

warn(
    "scrapers.infobox.extraction.service.strategy is deprecated; use "
    "scrapers.infobox.extraction.service.strategy_orchestrator",
    DeprecationWarning,
    stacklevel=2,
)

StrategyBackedInfoboxExtractionService = StrategyBackedInfoboxOrchestrator

__all__ = [
    "StrategyBackedInfoboxExtractionService",
    "StrategyBackedInfoboxOrchestrator",
]
