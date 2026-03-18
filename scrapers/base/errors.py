from dataclasses import KW_ONLY
from dataclasses import dataclass


@dataclass(eq=False)
class ScraperError(Exception):
    """Bazowy wyjątek domenowy dla scraperów."""

    message: str
    _: KW_ONLY
    url: str | None = None
    cause: Exception | None = None
    critical: bool = True

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        details = self.message
        if self.url:
            details = f"{details} (url={self.url})"
        return details


@dataclass(eq=False)
class ScraperNetworkError(ScraperError):
    """Błąd sieci (krytyczny)."""


@dataclass(eq=False)
class ScraperParseError(ScraperError):
    """Błąd parsowania (krytyczny)."""


@dataclass(eq=False)
class DomainParseError(ScraperError):
    """Błąd parsowania danych domenowych (niekrytyczny)."""

    critical: bool = False


@dataclass(eq=False)
class ScraperValidationError(ScraperError):
    """Błąd walidacji rekordów (krytyczny)."""


@dataclass(eq=False)
class ScraperNotFoundError(ScraperError):
    """Brak wymaganych elementów strony (niekrytyczny)."""

    critical: bool = False
