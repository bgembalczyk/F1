from __future__ import annotations

import warnings

from scrapers.services.domain_record.constructor_adapter import ConstructorDomainRecordInput
from scrapers.services.domain_record.constructor_adapter import ConstructorPipelineService

warnings.warn(
    "Module 'domain_record.constructor' is deprecated; use 'domain_record.constructor_adapter'.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ConstructorPipelineService", "ConstructorDomainRecordInput"]
