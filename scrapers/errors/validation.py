from dataclasses import dataclass

from scrapers.errors.base import ScraperError
from scrapers.errors.category import ErrorCategory


@dataclass(eq=False)
class ScraperValidationError(ScraperError):
    """Błąd walidacji rekordów (krytyczny)."""

    category: ErrorCategory = ErrorCategory.VALIDATION
    code: str = "validation.error"
    domain: str = "validation"
