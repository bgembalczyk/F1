from __future__ import annotations

import warnings
from abc import ABC
from typing import Any
from typing import Protocol
from typing import TypeAlias
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
BundleT_co = TypeVar("BundleT_co", bound="ParserBundle", covariant=True)
SectionResultT_co = TypeVar("SectionResultT_co", covariant=True)


@runtime_checkable
class HtmlElementParser(Protocol[ParsedDataT_co]):
    """Parser pojedynczego elementu HTML (Tag -> ParsedData)."""

    def parse(self, element: Tag) -> ParsedDataT_co: ...


SectionParserBase: TypeAlias = Parser[BeautifulSoup, SectionParseResult]


@runtime_checkable
class SectionParserProtocol(Protocol[SectionResultT_co]):
    """Typing-only parser contract for section fragments."""

    def parse(self, fragment: Any) -> SectionResultT_co: ...


@runtime_checkable
class RowMapper(Protocol[RowInputT_contra, RecordT_co]):
    """Mapowanie pojedynczego wiersza tabeli do rekordu domenowego."""

    def map_row(self, row: RowInputT_contra) -> RecordT_co | None: ...


@runtime_checkable
class TableMapper(Protocol[TableInputT_contra, RecordT_co]):
    """Mapowanie całej tabeli do rekordów domenowych."""

    def map_table(self, table: TableInputT_contra) -> list[RecordT_co]: ...


class ParserBundle(ABC):
    """Kompozycja parserów i komponentów pomocniczych."""


@runtime_checkable
class ParserProvider(Protocol[BundleT_co]):
    """Fabryka parserów zwracająca dedykowany ParserBundle."""

    def build(self, **kwargs: Any) -> BundleT_co: ...


def __getattr__(name: str) -> Any:
    if name == "SectionParser":
        warnings.warn(
            "roles.SectionParser is deprecated; use roles.SectionParserProtocol.",
            DeprecationWarning,
            stacklevel=2,
        )
        return SectionParserProtocol
    raise AttributeError(name)


__all__ = [
    "HtmlElementParser",
    "SectionParserProtocol",
    "RowMapper",
    "TableMapper",
    "ParserProvider",
    "ParserBundle",
    "SectionParseResult",
]
