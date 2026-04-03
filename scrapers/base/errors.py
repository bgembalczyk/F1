from dataclasses import KW_ONLY
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict

from scrapers.base.error_codes import resolve_error_code


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
class ScraperError(RuntimeError):
    """Bazowy wyjątek domenowy dla scraperów."""

    message: str
    _: KW_ONLY
    code: str = "pipeline.error"
    domain: str = "scrapers"
    source_name: str | None = None
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
        if self.code:
            context.append(f"code={self.code}")
        if self.domain:
            context.append(f"domain={self.domain}")
        if self.source_name:
            context.append(f"source_name={self.source_name}")
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
        code_definition = resolve_error_code(self.code)
        return ScraperErrorPayload(
            code=self.code,
            code_id=code_definition.code_id,
            code_description=code_definition.short_description,
            message=self.message,
            domain=self.domain,
            source_name=self.source_name,
            cause=str(self.cause) if self.cause else None,
            category=self.category.value,
            behavior=self.behavior.value,
            critical=self.critical,
            url=self.url,
            section_id=self.section_id,
            parser_name=self.parser_name,
            run_id=self.run_id,
        )

    @property
    def behavior(self) -> ErrorBehavior:
        return ERROR_BEHAVIOR_BY_CATEGORY.get(
            self.category,
            ErrorBehavior.HARD if self.critical else ErrorBehavior.SOFT,
        )


class ScraperErrorPayload(TypedDict):
    """Typed payload for exporting scraper exceptions to pipeline logs."""

    code: str
    code_id: str
    code_description: str
    message: str
    domain: str
    source_name: str | None
    cause: str | None
    category: str
    behavior: str
    critical: bool
    url: str | None
    section_id: str | None
    parser_name: str | None
    run_id: str | None


@dataclass(eq=False)
class ScraperNetworkError(ScraperError):
    """Błąd sieci (krytyczny)."""

    category: ErrorCategory = ErrorCategory.NETWORK
    code: str = "transport.error"
    domain: str = "network"


@dataclass(eq=False)
class ScraperParseError(ScraperError):
    """Błąd parsowania (krytyczny)."""

    category: ErrorCategory = ErrorCategory.PARSE
    code: str = "source.parse_error"
    domain: str = "parsing"


@dataclass(eq=False)
class DomainParseError(ScraperError):
    """Błąd parsowania danych domenowych (niekrytyczny)."""

    category: ErrorCategory = ErrorCategory.DOMAIN
    critical: bool = False
    code: str = "source.domain_parse_error"
    domain: str = "domain"


@dataclass(eq=False)
class ScraperValidationError(ScraperError):
    """Błąd walidacji rekordów (krytyczny)."""

    category: ErrorCategory = ErrorCategory.VALIDATION
    code: str = "validation.error"
    domain: str = "validation"


@dataclass(eq=False)
class ScraperNotFoundError(ScraperError):
    """Brak wymaganych elementów strony (niekrytyczny)."""

    category: ErrorCategory = ErrorCategory.DOMAIN
    critical: bool = False
    code: str = "source.not_found"
    domain: str = "domain"


@dataclass(eq=False)
class PipelineError(ScraperError):
    """Znormalizowany błąd przekazywany między warstwami pipeline."""

    code: str = "pipeline.error"
    domain: str = "pipeline"


@dataclass(eq=False)
class SourceParseError(PipelineError):
    code: str = "source.parse_error"
    domain: str = "parsing"
    category: ErrorCategory = ErrorCategory.PARSE


@dataclass(eq=False)
class ValidationError(PipelineError):
    code: str = "validation.error"
    domain: str = "validation"
    category: ErrorCategory = ErrorCategory.VALIDATION


@dataclass(eq=False)
class TransportError(PipelineError):
    code: str = "transport.error"
    domain: str = "network"
    category: ErrorCategory = ErrorCategory.NETWORK


def normalize_pipeline_error(
    exc: Exception,
    *,
    code: str = "pipeline.error",
    message: str = "Pipeline execution failed.",
    domain: str = "pipeline",
    source_name: str | None = None,
) -> PipelineError:
    if isinstance(exc, PipelineError):
        if source_name is not None and exc.source_name is None:
            exc.source_name = source_name
        return exc
    if isinstance(exc, ScraperParseError):
        return SourceParseError(
            message=exc.message,
            source_name=source_name or exc.source_name or exc.parser_name,
            cause=exc.cause or exc,
            url=exc.url,
            section_id=exc.section_id,
            parser_name=exc.parser_name,
            run_id=exc.run_id,
        )
    if isinstance(exc, ScraperValidationError):
        return ValidationError(
            message=exc.message,
            source_name=source_name or exc.source_name or exc.parser_name,
            cause=exc.cause or exc,
            url=exc.url,
            section_id=exc.section_id,
            parser_name=exc.parser_name,
            run_id=exc.run_id,
        )
    if isinstance(exc, ScraperNetworkError):
        return TransportError(
            message=exc.message,
            source_name=source_name or exc.source_name or exc.parser_name,
            cause=exc.cause or exc,
            url=exc.url,
            section_id=exc.section_id,
            parser_name=exc.parser_name,
            run_id=exc.run_id,
        )
    return PipelineError(
        message=message,
        code=code,
        domain=domain,
        source_name=source_name,
        cause=exc,
    )
