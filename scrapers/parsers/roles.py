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


class HtmlTagParserABC(ParserABC[Tag, TagOutT], ABC, Generic[TagOutT]):
    """Runtime contract for single HTML tag parsers (Tag -> payload)."""

    @abstractmethod
    def parse(self, raw: Tag) -> TagOutT: ...


class HtmlElementParserABC(HtmlTagParserABC[TagOutT], ABC, Generic[TagOutT]):
    """Canonical ABC for parsers of HTML elements (single Tag input)."""


class HtmlElementParserABC(HtmlTagParserABC[dict[str, Any]], ABC):
    """Legacy alias for tag -> dict parser contract."""


class SoupParserABC(ParserABC[BeautifulSoup, SoupOutT], ABC, Generic[SoupOutT]):
    """Parser dokumentu/fragmentu soup (BeautifulSoup -> payload)."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> SoupOutT: ...


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


class ListParserABC(ListHtmlParserABC, ABC):
    """Compatibility alias for list parsers."""


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


class ParseGroupMixin(ABC, Generic[TableInputT_contra, RecordT_co]):
    @abstractmethod
    def parse_group(self, table: TableInputT_contra) -> list[RecordT_co]: ...


class GroupParsingMixin(ParseGroupMixin[TableInputT_contra, RecordT_co], ABC):
    """Backward-compatible alias for parse_group capability."""


class ParsingBundle(ABC):
    """Kompozycja parserów i komponentów pomocniczych."""


class ParsingBundleProviderABC(ABC, Generic[BundleT_co]):
    @abstractmethod
    def build(self, **kwargs: Any) -> BundleT_co: ...


SoupDocumentParserABC = SoupParserABC


__all__ = [
    "GroupParsingMixin",
    "ParseGroupMixin",
    "HtmlElementParserABC",
    "HtmlTagParserABC",
    "InfoboxHtmlParserABC",
    "ListHtmlParserABC",
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
