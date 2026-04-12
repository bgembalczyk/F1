from dataclasses import dataclass

from scrapers.errors.base import ScraperError
from scrapers.errors.category import ErrorCategory


@dataclass(eq=False)
class ScraperNotFoundError(ScraperError):
    """Brak wymaganych elementów strony (niekrytyczny)."""

    category: ErrorCategory = ErrorCategory.DOMAIN
    critical: bool = False
    code: str = "source.not_found"
    domain: str = "domain"
