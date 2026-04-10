"""Canonical pipeline-service module for circuits domain."""

from scrapers.services.domain_record.circuit_pipeline_service import CircuitPipelineService


class CircuitsPipelineService(CircuitPipelineService):
    """Canonical class alias aligned with module naming standard."""


__all__ = ["CircuitsPipelineService", "CircuitPipelineService"]
