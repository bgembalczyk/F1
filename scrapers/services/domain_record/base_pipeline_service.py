from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from scrapers.core.domain_roles import Scraper
from scrapers.mixins.pipeline_mixins import DebugDumpMixin
from scrapers.mixins.pipeline_mixins import RetryMixin
from scrapers.mixins.pipeline_mixins import ValidationMixin
from scrapers.services.domain_record.base import DomainPipelineService

InputDTO = TypeVar("InputDTO")
PayloadT = TypeVar("PayloadT")


class BaseFactoryScraper(
    Scraper[dict[str, Any], dict[str, Any]],
    RetryMixin,
    DebugDumpMixin,
    ValidationMixin,
    ABC,
    Generic[PayloadT],
):
    """Backward-compatible alias around the canonical DomainPipelineService."""

    class BaseAssemblerPipelineService(
    DomainPipelineService[InputDTO, PayloadT, dict[str, Any]],
    Generic[InputDTO, PayloadT],
):
    """Backward-compatible alias around the canonical DomainPipelineService."""
