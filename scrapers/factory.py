from __future__ import annotations

import warnings

from scrapers.wiring.factory import ScraperFactory

warnings.warn(
    "scrapers.factory is deprecated and will be removed after the transition period; "
    "use scrapers.wiring.factory instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ScraperFactory"]
