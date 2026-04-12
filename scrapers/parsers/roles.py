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

In = TypeVar("In")
Out = TypeVar("Out")
TagOut = TypeVar("TagOut", covariant=True)
SoupOut = TypeVar("SoupOut", covariant=True)
RecordT_co = TypeVar("RecordT_co", covariant=True)
RowInputT_contra = TypeVar("RowInputT_contra", contravariant=True)
TableInputT_contra = TypeVar("TableInputT_contra", contravariant=True)
BundleT_co = TypeVar("BundleT_co", bound="ParsingBundle", covariant=True)


class ParserABC(Parser[In, Out], ABC, Generic[In, Out]):
    """Canonical parser contract (input -> output)."""

    @abstractmethod
    def parse(self, raw: In) -> Out: ...


class HtmlTagParserABC(ParserABC[Tag, TagOut], ABC, Generic[TagOut]):
    """Runtime contract for single HTML tag parsers (Tag -> payload)."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


class HtmlElementParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Canonical ABC for parsers of HTML elements (single Tag input)."""


class SoupParserABC(ParserABC[BeautifulSoup, SoupOut], ABC, Generic[SoupOut]):
    """Parser dokumentu/fragmentu soup (BeautifulSoup -> payload)."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SoupOut: ...


class SectionParserABC(ParserABC[BeautifulSoup, SectionParseResult], ABC):
    """Canonical ABC for section parsers."""


class SectionStructureParserABC(SectionParserABC, ABC):
    """Backward-compatible alias for section parser hierarchy."""


class TableHtmlParserABC(HtmlElementParserABC[dict[str, Any]], ABC):
    """ABC parsera tabeli HTML."""


class InfoboxHtmlParserABC(HtmlElementParserABC[dict[str, Any]], ABC):
    """ABC parsera infoboxa HTML."""


class ListHtmlParserABC(HtmlElementParserABC[dict[str, Any]], ABC):
    """ABC parsera listy HTML."""


class MapperABC(ABC, Generic[In, Out]):
    """Canonical mapper contract (input -> output)."""

    @abstractmethod
    def map(self, raw: In) -> Out: ...


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


SoupDocumentParserABC = SoupParserABC


__all__ = [
    "GroupParsingMixin",
    "HtmlElementParserABC",
    "HtmlTagParserABC",
    "InfoboxHtmlParserABC",
    "ListHtmlParserABC",
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
