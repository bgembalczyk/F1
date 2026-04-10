from __future__ import annotations

import warnings

from scrapers.runners.scraper_runner import ScraperRunner

warnings.warn(
    "scrapers.runner is deprecated; use scrapers.runners.scraper_runner instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ScraperRunner"]
