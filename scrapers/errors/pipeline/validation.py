from dataclasses import dataclass

from scrapers.errors.category import ErrorCategory
from scrapers.errors.pipeline.base import PipelineError


@dataclass(eq=False)
class ValidationError(PipelineError):
    code: str = "validation.error"
    domain: str = "validation"
    category: ErrorCategory = ErrorCategory.VALIDATION
