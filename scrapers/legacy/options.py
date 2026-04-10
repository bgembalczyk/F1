import warnings

from scrapers.core.options import ScraperOptions

warnings.warn(
    "scrapers.legacy.options is deprecated; use scrapers.core.options",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ScraperOptions"]
