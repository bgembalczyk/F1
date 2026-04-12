from dataclasses import dataclass

from scrapers.errors.base import ScraperError
from scrapers.errors.category import ErrorCategory


@dataclass(eq=False)
class ScraperParseError(ScraperError):
    """Błąd parsowania (krytyczny)."""

    category: ErrorCategory = ErrorCategory.PARSE
    code: str = "source.parse_error"
    domain: str = "parsing"
