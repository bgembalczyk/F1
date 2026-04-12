from dataclasses import dataclass

from scrapers.errors.base import ScraperError
from scrapers.errors.category import ErrorCategory


@dataclass(eq=False)
class ScraperNetworkError(ScraperError):
    """Błąd sieci (krytyczny)."""

    category: ErrorCategory = ErrorCategory.NETWORK
    code: str = "transport.error"
    domain: str = "network"
