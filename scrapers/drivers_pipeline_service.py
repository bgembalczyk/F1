"""Canonical pipeline-service module for drivers domain."""

from scrapers.services.domain_record.driver_pipeline_service import DriverPipelineService


class DriversPipelineService(DriverPipelineService):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["DriversPipelineService", "DriverPipelineService"]
