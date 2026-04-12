from abc import ABC
from abc import abstractmethod
from typing import Any


class MatchesMixin(ABC):
    @abstractmethod
    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool: ...
