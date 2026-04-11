from __future__ import annotations

import warnings

from scrapers.contracts.protocols_wiki import DiscoveredListScraperClassProtocol
from scrapers.contracts.protocols_wiki import DiscoveredRunnerClassProtocol
from scrapers.contracts.protocols_wiki import DiscoveredRunnerProtocol
from scrapers.contracts.protocols_wiki import ListScraperConfigProtocol

warnings.warn(
    "scrapers.protocols_wiki is deprecated and will be removed after the transition period; "
    "use scrapers.contracts.protocols_wiki instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DiscoveredListScraperClassProtocol",
    "DiscoveredRunnerClassProtocol",
    "DiscoveredRunnerProtocol",
    "ListScraperConfigProtocol",
]
