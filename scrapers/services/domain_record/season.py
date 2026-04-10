from __future__ import annotations

import warnings

from scrapers.services.domain_record.season_pipeline_service import SeasonDomainRecordInput
from scrapers.services.domain_record.season_pipeline_service import SeasonPipelineService

_DEPRECATION_MESSAGE = (
    "scrapers.services.domain_record.season is deprecated; "
    "import from scrapers.services.domain_record.season_pipeline_service instead."
)


def __getattr__(name: str):
    if name in {"DomainRecordService", "SeasonDomainRecordService"}:
        warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        return SeasonPipelineService
    raise AttributeError(name)


__all__ = ["DomainRecordService", "SeasonDomainRecordService", "SeasonDomainRecordInput"]
