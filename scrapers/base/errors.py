from dataclasses import KW_ONLY
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class ErrorCategory(str, Enum):
    NETWORK = "network"
    PARSE = "parse"
    VALIDATION = "validation"
    DOMAIN = "domain"


class ErrorBehavior(str, Enum):
    SOFT = "soft"
    HARD = "hard"


ERROR_BEHAVIOR_BY_CATEGORY: dict[ErrorCategory, ErrorBehavior] = {
    ErrorCategory.NETWORK: ErrorBehavior.HARD,
    ErrorCategory.PARSE: ErrorBehavior.HARD,
    ErrorCategory.VALIDATION: ErrorBehavior.HARD,
    ErrorCategory.DOMAIN: ErrorBehavior.SOFT,
}


@dataclass(eq=False)
class ScraperError(Exception):
    """Bazowy wyjątek domenowy dla scraperów."""

    message: str
    _: KW_ONLY
    url: str | None = None
    section_id: str | None = None
    parser_name: str | None = None
    run_id: str | None = None
    cause: Exception | None = None
    category: ErrorCategory = ErrorCategory.PARSE
    critical: bool = True

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        details = self.message
        context: list[str] = []
        if self.url:
            context.append(f"url={self.url}")
        if self.section_id:
            context.append(f"section_id={self.section_id}")
        if self.parser_name:
            context.append(f"parser_name={self.parser_name}")
        if self.run_id:
            context.append(f"run_id={self.run_id}")
        if context:
            details = f"{details} ({', '.join(context)})"
        return details

    def to_payload(self) -> "ScraperErrorPayload":
        return ScraperErrorPayload(
            message=self.message,
            category=self.category.value,
            behavior=self.behavior.value,
            critical=self.critical,
            url=self.url,
            section_id=self.section_id,
            parser_name=self.parser_name,
            run_id=self.run_id,
            cause=str(self.cause) if self.cause else None,
        )

    @property
    def behavior(self) -> ErrorBehavior:
        return ERROR_BEHAVIOR_BY_CATEGORY.get(
            self.category,
            ErrorBehavior.HARD if self.critical else ErrorBehavior.SOFT,
        )


class ScraperErrorPayload(TypedDict):
    """Typed payload for exporting scraper exceptions to pipeline logs."""

    message: str
    category: str
    behavior: str
    critical: bool
    url: str | None
    section_id: str | None
    parser_name: str | None
    run_id: str | None
    cause: str | None


@dataclass(eq=False)
class ScraperNetworkError(ScraperError):
    """Błąd sieci (krytyczny)."""

    category: ErrorCategory = ErrorCategory.NETWORK


@dataclass(eq=False)
class ScraperParseError(ScraperError):
    """Błąd parsowania (krytyczny)."""

    category: ErrorCategory = ErrorCategory.PARSE


@dataclass(eq=False)
class DomainParseError(ScraperError):
    """Błąd parsowania danych domenowych (niekrytyczny)."""

    category: ErrorCategory = ErrorCategory.DOMAIN
    critical: bool = False


@dataclass(eq=False)
class ScraperValidationError(ScraperError):
    """Błąd walidacji rekordów (krytyczny)."""

    category: ErrorCategory = ErrorCategory.VALIDATION


@dataclass(eq=False)
class ScraperNotFoundError(ScraperError):
    """Brak wymaganych elementów strony (niekrytyczny)."""

    category: ErrorCategory = ErrorCategory.DOMAIN
    critical: bool = False
