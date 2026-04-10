from __future__ import annotations

import warnings

from scrapers.services.domain_record.circuit_adapter import CircuitDomainRecordInput
from scrapers.services.domain_record.circuit_adapter import CircuitPipelineService

warnings.warn(
    "Module 'domain_record.circuit' is deprecated; use 'domain_record.circuit_adapter'.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["CircuitPipelineService", "CircuitDomainRecordInput"]
