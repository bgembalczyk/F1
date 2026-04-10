from __future__ import annotations

import warnings

from scrapers.services.domain_record.base_adapter import BaseAssemblerPipelineService

warnings.warn(
    "Module 'base_pipeline_service' is deprecated; use 'base_adapter' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["BaseAssemblerPipelineService"]
