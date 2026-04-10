from __future__ import annotations

from warnings import warn

from .circuit_extractor import CircuitInfoboxExtractionStrategy
from .circuit_extractor import CircuitInfoboxExtractor

warn(
    "scrapers.infobox.extraction.extractor.circuit is deprecated; use "
    "scrapers.infobox.extraction.extractor.circuit_extractor",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["CircuitInfoboxExtractionStrategy", "CircuitInfoboxExtractor"]
