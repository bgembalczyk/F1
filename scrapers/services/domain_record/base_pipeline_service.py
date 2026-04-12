from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from scrapers.services.domain_record.base import DomainPipelineService

InputDTO = TypeVar("InputDTO")
PayloadT = TypeVar("PayloadT")


class BaseDomainPipelineService(
    DomainPipelineService[InputDTO, PayloadT, dict[str, Any]],
    Generic[InputDTO, PayloadT],
):
    """Canonicalna baza pipeline service dla rekordów domenowych."""


__all__ = ["BaseDomainPipelineService"]
