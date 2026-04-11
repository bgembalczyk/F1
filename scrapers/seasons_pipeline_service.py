"""Canonical pipeline-service module for seasons domain."""

from scrapers.services.domain_record.season_pipeline_service import (
    SeasonPipelineService,
)


class SeasonsPipelineService(SeasonPipelineService):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["SeasonsPipelineService", "SeasonPipelineService"]
