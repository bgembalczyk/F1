from __future__ import annotations

from warnings import warn

from scrapers.infobox.extraction.protocol import InfoboxExtractionService

warn(
    "scrapers.infobox.extraction.service.protocol is deprecated; use "
    "scrapers.infobox.extraction.protocol",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["InfoboxExtractionService"]
