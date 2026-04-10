from __future__ import annotations

import warnings

from scrapers.services.domain_record.driver_adapter import DriverDomainRecordInput
from scrapers.services.domain_record.driver_adapter import DriverPipelineService

warnings.warn(
    "Module 'domain_record.driver' is deprecated; use 'domain_record.driver_adapter'.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DriverPipelineService", "DriverDomainRecordInput"]
