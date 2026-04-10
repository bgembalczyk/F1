from __future__ import annotations

import warnings

from scrapers.contracts.protocols_wiki import DiscoveredListScraperClassProtocol, DiscoveredRunnerClassProtocol, DiscoveredRunnerProtocol, ListScraperConfigProtocol

warnings.warn(
    "scrapers.protocols_wiki is deprecated and will be removed after the transition period; "
    "use scrapers.contracts.protocols_wiki instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DiscoveredListScraperClassProtocol", "DiscoveredRunnerClassProtocol", "DiscoveredRunnerProtocol", "ListScraperConfigProtocol"]
