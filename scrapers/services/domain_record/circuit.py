from __future__ import annotations

import warnings

from scrapers.services.domain_record.circuit_pipeline_service import CircuitDomainRecordInput
from scrapers.services.domain_record.circuit_pipeline_service import CircuitPipelineService

_DEPRECATION_MESSAGE = (
    "scrapers.services.domain_record.circuit is deprecated; "
    "import from scrapers.services.domain_record.circuit_pipeline_service instead."
)


def __getattr__(name: str):
    if name in {"DomainRecordService", "CircuitDomainRecordService"}:
        warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        return CircuitPipelineService
    raise AttributeError(name)


__all__ = ["DomainRecordService", "CircuitDomainRecordService", "CircuitDomainRecordInput"]
