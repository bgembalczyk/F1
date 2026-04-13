from dataclasses import dataclass

from scrapers.errors.category import ErrorCategory
from scrapers.errors.pipeline.base import PipelineError


@dataclass(eq=False)
class TransportError(PipelineError):
    code: str = "transport.error"
    domain: str = "network"
    category: ErrorCategory = ErrorCategory.NETWORK
