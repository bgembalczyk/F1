"""Canonical pipeline-service module for constructors domain."""

from scrapers.services.domain_record.constructor_pipeline_service import (
    ConstructorPipelineService,
)


class ConstructorsPipelineService(ConstructorPipelineService):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["ConstructorsPipelineService", "ConstructorPipelineService"]
