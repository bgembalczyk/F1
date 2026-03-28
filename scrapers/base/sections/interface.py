from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Protocol
from typing import TypeAlias
from typing import TypeVar
from typing import runtime_checkable

from models.value_objects import EntityName
from models.value_objects import SectionId
from models.value_objects import WikiUrl

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter

SectionValue: TypeAlias = object
SectionRecord: TypeAlias = dict[str, SectionValue]
SectionMetadata: TypeAlias = dict[str, SectionValue]


@dataclass(frozen=True)
class SectionParseResult:
    """Unified output for domain section parsers."""

    section_id: SectionId
    section_label: EntityName
    records: list[SectionRecord]
    metadata: SectionMetadata

    def __post_init__(self) -> None:
        object.__setattr__(self, "section_id", SectionId.from_raw(self.section_id))
        object.__setattr__(
            self,
            "section_label",
            EntityName.from_raw(self.section_label),
        )


@runtime_checkable
class SectionParser(Protocol):
    """Common section parser interface.

    Input: BeautifulSoup fragment scoped to a section.
    Output: parsed records with section-level metadata.
    """

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult: ...


class SectionTextParser(Protocol):
    """Common parser interface for narrative/text section content."""

    def parse(self, section_fragment: BeautifulSoup) -> list[SectionRecord]: ...


class SectionTableParser(Protocol):
    """Common parser interface for table-oriented section content."""

    def parse(self, section_fragment: BeautifulSoup) -> list[SectionRecord]: ...


ServiceT_co = TypeVar("ServiceT_co", covariant=True)


class SectionServiceFactory(Protocol[ServiceT_co]):
    """Factory contract for building section services in single-article scrapers."""

    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: WikiUrl | str | None = None,
    ) -> ServiceT_co: ...
