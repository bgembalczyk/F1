from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol
from typing import TypeVar

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter


@dataclass(frozen=True)
class SectionParseResult:
    """Unified output for domain section parsers."""

    section_id: str
    section_label: str
    records: list[dict[str, Any]]
    metadata: dict[str, Any]


class SectionParser(Protocol):
    """Common section parser interface.

    Input: BeautifulSoup fragment scoped to a section.
    Output: parsed records with section-level metadata.
    """

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult: ...


class SectionTextParser(Protocol):
    """Common parser interface for narrative/text section content."""

    def parse(self, section_fragment: BeautifulSoup) -> list[dict[str, Any]]: ...


class SectionTableParser(Protocol):
    """Common parser interface for table-oriented section content."""

    def parse(self, section_fragment: BeautifulSoup) -> list[dict[str, Any]]: ...


ServiceT = TypeVar("ServiceT")


class SectionServiceFactory(Protocol[ServiceT]):
    """Factory contract for building section services in single-article scrapers."""

    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: str | None = None,
    ) -> ServiceT: ...
