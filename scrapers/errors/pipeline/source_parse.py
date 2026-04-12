from dataclasses import dataclass

from scrapers.errors.category import ErrorCategory
from scrapers.errors.pipeline.base import PipelineError


@dataclass(eq=False)
class SourceParseError(PipelineError):
    code: str = "source.parse_error"
    domain: str = "parsing"
    category: ErrorCategory = ErrorCategory.PARSE
