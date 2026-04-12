from dataclasses import KW_ONLY
from dataclasses import dataclass

from scrapers.error_codes import resolve_error_code
from scrapers.errors.behavior import ERROR_BEHAVIOR_BY_CATEGORY
from scrapers.errors.behavior import ErrorBehavior
from scrapers.errors.category import ErrorCategory
from scrapers.errors.payload import ScraperErrorPayload


@dataclass(eq=False)
class ScraperError(RuntimeError):
    """Bazowy wyjątek domenowy dla scraperów."""

    message: str
    _: KW_ONLY
    code: str = "pipeline.error"
    domain: str = "scrapers"
    level: str = "error"
    source_name: str | None = None
    record: str | None = None
    suggestion: str | None = None
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
            level=self.level,
            code_id=code_definition.code_id,
            code_description=code_definition.short_description,
            message=self.message,
            domain=self.domain,
            source=self.source_name or self.parser_name,
            record=self.record,
            suggestion=self.suggestion,
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

