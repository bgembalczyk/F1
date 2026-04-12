from abc import ABC
from abc import abstractmethod

from scrapers.columns.context import ColumnContext


class ConstructorPartParserABC(ABC):
    @abstractmethod
    def __init__(self, index: int) -> None: ...

    @abstractmethod
    def parse(self, ctx: ColumnContext) -> dict[str, object] | None: ...


ConstructorPartParser = ConstructorPartParserABC

__all__ = ["ConstructorPartParser", "ConstructorPartParserABC"]
