from __future__ import annotations

import warnings

from scrapers.wiring.runtime.factory import ScraperRuntimeFactory

warnings.warn(
    "scrapers.runtime.factory is deprecated and will be removed after the transition period; "
    "use scrapers.wiring.runtime.factory instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ScraperRuntimeFactory"]
