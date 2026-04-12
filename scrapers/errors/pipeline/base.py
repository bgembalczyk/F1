from dataclasses import dataclass

from scrapers.errors.base import ScraperError


@dataclass(eq=False)
class PipelineError(ScraperError):
    """Znormalizowany błąd przekazywany między warstwami pipeline."""

    code: str = "pipeline.error"
    domain: str = "pipeline"
