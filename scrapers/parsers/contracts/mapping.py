from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

InT = TypeVar("InT")
OutT = TypeVar("OutT")
RecordT_co = TypeVar("RecordT_co", covariant=True)
RowInputT_contra = TypeVar("RowInputT_contra", contravariant=True)
TableInputT_contra = TypeVar("TableInputT_contra", contravariant=True)


class MapperABC(ABC, Generic[InT, OutT]):
    """Canonical mapper contract (input -> output)."""

    @abstractmethod
    def map(self, raw: InT) -> OutT: ...


class TableDomainMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    @abstractmethod
    def map(self, fragment: dict[str, Any]) -> dict[str, Any] | None: ...


class TableMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    """Mapper fragmentu tabeli na dane domenowe."""

    @abstractmethod
    def map(self, fragment: dict[str, Any]) -> dict[str, Any] | None: ...


class MatchesMixin(ABC):
    @abstractmethod
    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool: ...


class RowMappingMixin(ABC, Generic[RowInputT_contra, RecordT_co]):
    @abstractmethod
    def map_row(self, row: RowInputT_contra) -> RecordT_co | None: ...


class ParseGroupMixin(ABC, Generic[TableInputT_contra, RecordT_co]):
    @abstractmethod
    def parse_group(self, table: TableInputT_contra) -> list[RecordT_co]: ...


class GroupParsingMixin(ParseGroupMixin[TableInputT_contra, RecordT_co], ABC):
    """Backward-compatible alias for parse_group capability."""


__all__ = [
    "GroupParsingMixin",
    "InT",
    "MapperABC",
    "MatchesMixin",
    "OutT",
    "ParseGroupMixin",
    "RecordT_co",
    "RowInputT_contra",
    "RowMappingMixin",
    "TableDomainMapperABC",
    "TableInputT_contra",
    "TableMapperABC",
]
