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

TagIn = TypeVar("TagIn", bound=Tag)
Out = TypeVar("Out")
ParsedDataT_co = TypeVar("ParsedDataT_co", covariant=True)
RowInputT_contra = TypeVar("RowInputT_contra", contravariant=True)
TableInputT_contra = TypeVar("TableInputT_contra", contravariant=True)
RecordT_co = TypeVar("RecordT_co", covariant=True)
BundleT_co = TypeVar("BundleT_co", bound="ParsingBundle", covariant=True)


class HtmlTagParserABC(Parser[TagIn, Out], ABC, Generic[TagIn, Out]):
    """Runtime contract for single HTML tag parsers (Tag -> parsed payload)."""

    @abstractmethod
    def parse(self, raw: TagIn) -> Out: ...


class SoupDocumentParserABC(Parser[BeautifulSoup, Out], ABC, Generic[Out]):
    """Runtime contract for soup/document parsers (BeautifulSoup -> output)."""

    @abstractmethod
    def parse(self, raw: BeautifulSoup) -> Out: ...


class SectionStructureParserABC(SoupDocumentParserABC[SectionParseResult], ABC):
    """Runtime contract for section structure parsers."""


class TableHtmlParserABC(Parser[dict[str, Any], dict[str, Any] | None], ABC):
    """Runtime contract for HTML table-fragment domain mappers."""

    @abstractmethod
    def parse(self, raw: dict[str, Any]) -> dict[str, Any] | None: ...


class InfoboxHtmlParserABC(HtmlTagParserABC[Tag, dict[str, Any]], ABC):
    """Runtime contract for infobox HTML parsers."""


class HtmlElementParserABC(HtmlTagParserABC[Tag, ParsedDataT_co], ABC, Generic[ParsedDataT_co]):
    """Backward-compatible alias for tag-level parser contracts."""


class SectionParserABC(SectionStructureParserABC):
    """Backward-compatible alias for section parser contracts."""


class TableDomainMapperABC(TableHtmlParserABC):
    """Backward-compatible alias for table parser contracts."""


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
    "HtmlElementParserABC",
    "HtmlTagParserABC",
    "InfoboxHtmlParserABC",
    "MatchesMixin",
    "ParsingBundle",
    "ParsingBundleProviderABC",
    "RowMappingMixin",
    "SectionParseResult",
    "SectionParserABC",
    "SectionStructureParserABC",
    "SoupDocumentParserABC",
    "TableDomainMapperABC",
    "TableHtmlParserABC",
]
