from __future__ import annotations

import warnings

from scrapers.runners.pipeline_runner import ERROR_FIX_LINKS
from scrapers.runners.pipeline_runner import ErrorSummaryWriter
from scrapers.runners.pipeline_runner import PipelineInput
from scrapers.runners.pipeline_runner import PipelineIssue
from scrapers.runners.pipeline_runner import PipelineResult
from scrapers.runners.pipeline_runner import PipelineStep
from scrapers.runners.pipeline_runner import ScraperPipelineRunner
from scrapers.runners.pipeline_runner import StepQualityWriter
from scrapers.runners.pipeline_runner import StepRunner

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
