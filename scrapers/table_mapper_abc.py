from abc import ABC
from abc import abstractmethod
from typing import Any

from scrapers.mapper_abc import MapperABC


class TableMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    """Mapper fragmentu tabeli na dane domenowe."""

    @abstractmethod
    def map(self, fragment: dict[str, Any]) -> dict[str, Any] | None: ...
