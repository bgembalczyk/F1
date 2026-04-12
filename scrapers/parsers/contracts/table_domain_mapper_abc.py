from abc import ABC
from abc import abstractmethod
from typing import Any

from scrapers.parsers.contracts.mapper_abc import MapperABC


class TableDomainMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    @abstractmethod
    def map(self, fragment: dict[str, Any]) -> dict[str, Any] | None: ...
