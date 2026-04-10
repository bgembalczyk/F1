import warnings

from scrapers.core.errors import DomainParseError
from scrapers.core.errors import ScraperNetworkError
from scrapers.core.errors import ScraperParseError
from scrapers.core.errors import normalize_pipeline_error

warnings.warn(
    "scrapers.legacy.errors is deprecated; use scrapers.core.errors",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DomainParseError",
    "ScraperNetworkError",
    "ScraperParseError",
    "normalize_pipeline_error",
]
