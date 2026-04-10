from __future__ import annotations

import warnings

from scrapers.services.domain_record.constructor_pipeline_service import (
    ConstructorDomainRecordInput,
)
from scrapers.services.domain_record.constructor_pipeline_service import (
    ConstructorPipelineService,
)

_DEPRECATION_MESSAGE = (
    "scrapers.services.domain_record.constructor is deprecated; "
    "import from scrapers.services.domain_record.constructor_pipeline_service instead."
)


def __getattr__(name: str):
    if name in {"DomainRecordService", "ConstructorDomainRecordService"}:
        warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        return ConstructorPipelineService
    raise AttributeError(name)


__all__ = [
    "DomainRecordService",
    "ConstructorDomainRecordService",
    "ConstructorDomainRecordInput",
]
