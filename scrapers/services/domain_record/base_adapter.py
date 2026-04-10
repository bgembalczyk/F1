from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from scrapers.services.domain_record.base import DomainPipelineService

InputDTO = TypeVar("InputDTO")
PayloadT = TypeVar("PayloadT")


class BaseAssemblerPipelineService(
    DomainPipelineService[InputDTO, PayloadT, dict[str, Any]],
    Generic[InputDTO, PayloadT],
):
    """Adapter bazowy dla pipeline'ów, które zwracają rekord ``dict``."""
