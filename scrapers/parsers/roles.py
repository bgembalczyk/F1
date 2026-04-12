from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.domain_roles import Parser
from scrapers.section.parse_results import SectionParseResult

InT = TypeVar("InT")
OutT = TypeVar("OutT")
TagOutT = TypeVar("TagOutT", covariant=True)
SoupOutT = TypeVar("SoupOutT", covariant=True)
RecordT_co = TypeVar("RecordT_co", covariant=True)
RowInputT_contra = TypeVar("RowInputT_contra", contravariant=True)
TableInputT_contra = TypeVar("TableInputT_contra", contravariant=True)
BundleT_co = TypeVar("BundleT_co", bound="ParsingBundle", covariant=True)


class ParserABC(Parser[InT, OutT], ABC, Generic[InT, OutT]):
    """Canonical parser contract (input -> output)."""

    @abstractmethod
    def parse(self, raw: InT) -> OutT: ...


class MapperABC(ABC, Generic[InT, OutT]):
    """Canonical mapper contract (input -> output)."""

    @abstractmethod
    def map(self, raw: InT) -> OutT: ...


class HtmlTagParserABC(ParserABC[Tag, TagOutT], ABC, Generic[TagOutT]):
    """Runtime contract for single HTML tag parsers (Tag -> parsed payload)."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOutT: ...


class SoupParserABC(ParserABC[BeautifulSoup, SoupOutT], ABC, Generic[SoupOutT]):
    """Parser dokumentu/fragmentu soup (BeautifulSoup -> payload)."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SoupOutT: ...


class SectionStructureParserABC(SoupParserABC[SectionParseResult], ABC):
    """Parser struktury sekcji (BeautifulSoup -> SectionParseResult)."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SectionParseResult: ...


class TableHtmlParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class TableDomainMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    @abstractmethod
    def map(self, fragment: dict[str, Any]) -> dict[str, Any] | None: ...


class InfoboxHtmlParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Runtime contract for infobox HTML parsers."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class ListHtmlParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser listy HTML."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class TableMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    """Mapper fragmentu tabeli na dane domenowe."""

    @abstractmethod
    def map(self, raw: dict[str, Any]) -> dict[str, Any] | None: ...


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


# Backward-compatible aliases.
HtmlElementParserABC = HtmlTagParserABC
ListParserABC = ListHtmlParserABC
SectionParserABC = SectionStructureParserABC
SoupDocumentParserABC = SoupParserABC


__all__ = [
    "GroupParsingMixin",
    "HtmlElementParserABC",
    "HtmlTagParserABC",
    "InfoboxHtmlParserABC",
    "ListHtmlParserABC",
    "ListParserABC",
    "MapperABC",
    "MatchesMixin",
    "ParserABC",
    "ParsingBundle",
    "ParsingBundleProviderABC",
    "RowMappingMixin",
    "SectionParseResult",
    "SectionParserABC",
    "SectionStructureParserABC",
    "SoupDocumentParserABC",
    "SoupParserABC",
    "TableDomainMapperABC",
    "TableHtmlParserABC",
    "TableMapperABC",
]
