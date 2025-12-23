from dataclasses import dataclass
from typing import Optional


@dataclass
class ScraperError(Exception):
    """Bazowy wyjątek domenowy dla scraperów."""

    message: str
    url: Optional[str] = None
    cause: Optional[Exception] = None
    critical: bool = True

    def __str__(self) -> str:
        details = self.message
        if self.url:
            details = f"{details} (url={self.url})"
        return details


class ScraperNetworkError(ScraperError):
    """Błąd sieci (krytyczny)."""


class ScraperParseError(ScraperError):
    """Błąd parsowania (krytyczny)."""


class ScraperNotFoundError(ScraperError):
    """Brak wymaganych elementów strony (niekrytyczny)."""

    def __init__(self, message: str, *, url: Optional[str] = None) -> None:
        self.message = message
        self.url = url
        self.cause = None
        self.critical = False
        Exception.__init__(self, message)
