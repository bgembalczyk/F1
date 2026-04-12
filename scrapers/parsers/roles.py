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
    """Parser pojedynczego elementu HTML (Tag -> payload)."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...


class SoupParserABC(ParserABC[BeautifulSoup, SoupOut], ABC, Generic[SoupOut]):
    """Parser dokumentu/fragmentu soup (BeautifulSoup -> payload)."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SoupOut: ...


class SectionStructureParserABC(SoupParserABC[SectionParseResult], ABC):
    """Parser struktury sekcji (BeautifulSoup -> SectionParseResult)."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SectionParseResult: ...


class TableHtmlParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser tabeli HTML (Tag -> fragment tabeli)."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class InfoboxHtmlParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser infoboxa HTML."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class ListHtmlParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Parser listy HTML."""

    @abstractmethod
    def parse(self, raw: Tag) -> dict[str, Any]: ...


class MapperABC(ABC, Generic[In, Out]):
    """Canonical mapper contract (input -> output)."""

    @abstractmethod
    def map(self, raw: In) -> Out: ...


class TableMapperABC(MapperABC[dict[str, Any], dict[str, Any] | None], ABC):
    """Mapper fragmentu tabeli na dane domenowe."""

    @abstractmethod
    def map(self, raw: dict[str, Any]) -> dict[str, Any] | None: ...


class MatchesMixin(ABC):
    """Mixin for parser classes exposing content matching behavior."""

    @abstractmethod
    def matches(self, raw: Any) -> bool: ...


class RowMappingMixin(ABC, Generic[RowInputT_contra, RecordT_co]):
    """Mixin for row-level mapping behavior."""

    @abstractmethod
    def map_row(self, row: RowInputT_contra) -> RecordT_co | None: ...


class GroupParsingMixin(ABC, Generic[TableInputT_contra, RecordT_co]):
    """Mixin for collection/group parsing behavior."""

    @abstractmethod
    def map_table(self, table: TableInputT_contra) -> list[RecordT_co]: ...


class ParsingBundle(ABC):
    """Kompozycja parserów i komponentów pomocniczych."""


class ParsingBundleProviderABC(ABC, Generic[BundleT_co]):
    @abstractmethod
    def build(self, **kwargs: Any) -> BundleT_co: ...


__all__ = [
    "GroupParsingMixin",
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
    "SectionStructureParserABC",
    "SoupParserABC",
    "TableHtmlParserABC",
    "TableMapperABC",
]
