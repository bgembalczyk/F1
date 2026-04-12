from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from scrapers.parsers.base_family import InfoboxParserABC
from scrapers.parsers.base_family import ListParserABC
from scrapers.parsers.base_family import SectionParserABC
from scrapers.parsers.base_family import SoupParserABC
from scrapers.parsers.base_family import TableParserABC
from scrapers.parsers.base_family import TagParserABC

InT = TypeVar("InT")
OutT = TypeVar("OutT")
RecordT_co = TypeVar("RecordT_co", covariant=True)
RowInputT_contra = TypeVar("RowInputT_contra", contravariant=True)
TableInputT_contra = TypeVar("TableInputT_contra", contravariant=True)
BundleT_co = TypeVar("BundleT_co", bound="ParsingBundle", covariant=True)


class MapperABC(ABC, Generic[InT, OutT]):
    @abstractmethod
    def map(self, raw: InT) -> OutT: ...


class TableDomainMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    @abstractmethod
    def map(self, fragment: dict[str, Any]) -> dict[str, Any] | None: ...


class TableMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    """Mapper fragmentu tabeli na dane domenowe."""


class MatchesMixin(ABC):
    @abstractmethod
    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool: ...


class RowMappingMixin(ABC, Generic[RowInputT_contra, RecordT_co]):
    @abstractmethod
    def map_row(self, row: RowInputT_contra) -> RecordT_co | None: ...


class GroupParsingMixin(ABC, Generic[TableInputT_contra, RecordT_co]):
    @abstractmethod
    def map_table(self, table: TableInputT_contra) -> list[RecordT_co]: ...


class ParsingBundle(ABC):
    """Kompozycja parserów i komponentów pomocniczych."""


class ParsingBundleProviderABC(ABC, Generic[BundleT_co]):
    @abstractmethod
    def build(self, **kwargs: Any) -> BundleT_co: ...


__all__ = [
    "GroupParsingMixin",
    "InfoboxParserABC",
    "ListParserABC",
    "MapperABC",
    "MatchesMixin",
    "ParsingBundle",
    "ParsingBundleProviderABC",
    "RowMappingMixin",
    "SectionParserABC",
    "SoupParserABC",
    "TableDomainMapperABC",
    "TableMapperABC",
    "TableParserABC",
    "TagParserABC",
]
