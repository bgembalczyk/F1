from __future__ import annotations

import warnings

from scrapers.wiring.composition_drivers import DriverScraperCompositionFactory, DriverScraperDependencies

warnings.warn(
    "scrapers.composition_drivers is deprecated and will be removed after the transition period; "
    "use scrapers.wiring.composition_drivers instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DriverScraperCompositionFactory", "DriverScraperDependencies"]
