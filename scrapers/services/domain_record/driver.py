from __future__ import annotations

import warnings

from scrapers.services.domain_record.driver_pipeline_service import DriverDomainRecordInput
from scrapers.services.domain_record.driver_pipeline_service import DriverPipelineService

_DEPRECATION_MESSAGE = (
    "scrapers.services.domain_record.driver is deprecated; "
    "import from scrapers.services.domain_record.driver_pipeline_service instead."
)


def __getattr__(name: str):
    if name in {"DomainRecordService", "DriverDomainRecordService"}:
        warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        return DriverPipelineService
    raise AttributeError(name)


__all__ = ["DomainRecordService", "DriverDomainRecordService", "DriverDomainRecordInput"]
