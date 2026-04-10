from __future__ import annotations

import warnings

from scrapers.runners.pipeline_runner import (
    ERROR_FIX_LINKS,
    ErrorSummaryWriter,
    PipelineInput,
    PipelineIssue,
    PipelineResult,
    PipelineStep,
    ScraperPipelineRunner,
    StepQualityWriter,
    StepRunner,
)

warnings.warn(
    "scrapers.pipeline_runner is deprecated; use scrapers.runners.pipeline_runner instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ERROR_FIX_LINKS",
    "ErrorSummaryWriter",
    "PipelineInput",
    "PipelineIssue",
    "PipelineResult",
    "PipelineStep",
    "ScraperPipelineRunner",
    "StepQualityWriter",
    "StepRunner",
]
