from abc import ABC
from abc import abstractmethod

from validation.validator_base import ExportRecord


class FieldnamesStrategyABC(ABC):
    @abstractmethod
    def resolve(
        self,
        data: list[ExportRecord],
        *,
        strategy: str,
    ) -> list[str]: ...


__all__ = ["FieldnamesStrategyABC"]
