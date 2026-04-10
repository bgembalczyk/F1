from __future__ import annotations

import warnings

from scrapers.services.domain_record.season_adapter import SeasonDomainRecordInput
from scrapers.services.domain_record.season_adapter import SeasonPipelineService

warnings.warn(
    "Module 'domain_record.season' is deprecated; use 'domain_record.season_adapter'.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["SeasonPipelineService", "SeasonDomainRecordInput"]
