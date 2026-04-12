from abc import ABC
from abc import abstractmethod
from typing import Any


class DataFrameFormatterABC(ABC):
    @abstractmethod
    def format(self, result: object) -> Any: ...


__all__ = ["DataFrameFormatterABC"]
