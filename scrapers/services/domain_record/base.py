from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

InputT = TypeVar("InputT")


class BaseDomainRecordService(ABC, Generic[InputT]):
    @abstractmethod
    def assemble_record(self, payload: InputT) -> dict[str, Any]:
        """Build final domain record from a single domain-specific DTO."""

