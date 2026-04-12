from __future__ import annotations

import warnings

from scrapers.protocols.protocols_wiki import DiscoveredListScraperClassABC
from scrapers.protocols.protocols_wiki import DiscoveredRunnerABC
from scrapers.protocols.protocols_wiki import DiscoveredRunnerClassABC
from scrapers.protocols.protocols_wiki import ListScraperConfigABC

warnings.warn(
    "scrapers.protocols_wiki is deprecated and will be removed after the transition period; "
    "use scrapers.protocols.protocols_wiki instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DiscoveredListScraperClassABC",
    "DiscoveredRunnerABC",
    "DiscoveredRunnerClassABC",
    "ListScraperConfigABC",
]
