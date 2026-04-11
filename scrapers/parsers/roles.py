from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar
from typing import runtime_checkable

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.domain_roles import Parser
from scrapers.section.parse_results import SectionParseResult

ParsedDataT_co = TypeVar("ParsedDataT_co", covariant=True)
RowInputT_contra = TypeVar("RowInputT_contra", contravariant=True)
TableInputT_contra = TypeVar("TableInputT_contra", contravariant=True)
RecordT_co = TypeVar("RecordT_co", covariant=True)
BundleT_co = TypeVar("BundleT_co", bound="ParsingBundle", covariant=True)


class HtmlElementParserABC(Parser[Tag, ParsedDataT_co], ABC, Generic[ParsedDataT_co]):
    """Runtime contract for single HTML element parsers (Tag -> parsed payload)."""

    @abstractmethod
    def parse(self, raw: Tag) -> ParsedDataT_co: ...


class SectionParserABC(Parser[BeautifulSoup, SectionParseResult], ABC):
    """Runtime contract for section parsers (BeautifulSoup -> SectionParseResult)."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SectionParseResult: ...


class TableDomainMapperABC(Parser[dict[str, Any], dict[str, Any] | None], ABC):
    """Runtime contract for table-fragment domain mappers."""

    @abstractmethod
    def parse(self, raw: dict[str, Any]) -> dict[str, Any] | None: ...


@runtime_checkable
class RowMapper(Protocol[RowInputT_contra, RecordT_co]):
    def map_row(self, row: RowInputT_contra) -> RecordT_co | None: ...


@runtime_checkable
class TableMapper(Protocol[TableInputT_contra, RecordT_co]):
    def map_table(self, table: TableInputT_contra) -> list[RecordT_co]: ...


class ParsingBundle(ABC):
    """Kompozycja parserów i komponentów pomocniczych."""


@runtime_checkable
class ParsingBundleProvider(Protocol[BundleT_co]):
    def build(self, **kwargs: Any) -> BundleT_co: ...


__all__ = [
    "HtmlElementParserABC",
    "SectionParserABC",
    "TableDomainMapperABC",
    "RowMapper",
    "TableMapper",
    "ParsingBundleProvider",
    "ParsingBundle",
    "SectionParseResult",
]
