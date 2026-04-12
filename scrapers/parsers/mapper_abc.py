from abc import ABC
from abc import abstractmethod
from typing import Generic

from scrapers.parsers.contracts.constants_contracts import InT
from scrapers.parsers.contracts.constants_contracts import OutT


class MapperABC(ABC, Generic[InT, OutT]):
    """Canonical mapper contract (input -> output)."""

    @abstractmethod
    def map(self, raw: InT) -> OutT: ...
