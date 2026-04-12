from scrapers.errors.network import ScraperNetworkError
from scrapers.errors.parse import ScraperParseError
from scrapers.errors.pipeline.base import PipelineError
from scrapers.errors.pipeline.source_parse import SourceParseError
from scrapers.errors.pipeline.transport import TransportError
from scrapers.errors.pipeline.validation import ValidationError
from scrapers.errors.validation import ScraperValidationError


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
