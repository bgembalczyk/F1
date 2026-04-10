from __future__ import annotations

import warnings

from scrapers.wiring.composition_seasons import SeasonScraperCompositionFactory, SeasonScraperDependencies

warnings.warn(
    "scrapers.composition_seasons is deprecated and will be removed after the transition period; "
    "use scrapers.wiring.composition_seasons instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["SeasonScraperCompositionFactory", "SeasonScraperDependencies"]
