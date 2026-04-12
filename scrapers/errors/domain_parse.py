from dataclasses import dataclass

from scrapers.errors.base import ScraperError
from scrapers.errors.category import ErrorCategory


@dataclass(eq=False)
class DomainParseError(ScraperError):
    """Błąd parsowania danych domenowych (niekrytyczny)."""

    category: ErrorCategory = ErrorCategory.DOMAIN
    critical: bool = False
    code: str = "source.domain_parse_error"
    domain: str = "domain"
