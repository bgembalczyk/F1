from abc import ABC
from abc import abstractmethod
from typing import Any


class InfoboxSectionDiscoveryABC(ABC):
    @abstractmethod
    def collect(self, table: object) -> list[dict[str, Any]]: ...


__all__ = ["InfoboxSectionDiscoveryABC"]
