from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable

if False:  # pragma: no cover
    from bs4 import BeautifulSoup

    from scrapers.section.parse_results import SectionParseResult


@runtime_checkable
class ListScraperContract(Protocol):
    """Minimal contract for list/seed scrapers.

    Required API:
    - ``fetch()`` as public extraction entrypoint.

    Extension rules:
    - additional domain hooks MUST be opt-in and keep ``fetch`` backward-compatible;
    - list-specific preprocessing should happen in protected methods
      (e.g. ``_parse_soup``), never by changing ``fetch`` return type.
    """

    def fetch(self) -> list[dict[str, Any]]: ...


@runtime_checkable
class TableScraperContract(Protocol):
    """Minimal contract for table-based scrapers.

    Required API:
    - ``parse_soup(soup)`` for table payload parsing;
    - ``parse_row(row)`` for row-level transformation.

    Extension rules:
    - subclasses should override parser hooks, not constructor wiring;
    - ``parse_row`` may return ``None`` for skipped rows, but never non-record
      control values.
    """

    def parse_soup(self, soup: BeautifulSoup) -> list[Any]: ...

    def parse_row(self, row: Any) -> Any | None: ...


@runtime_checkable
class SingleArticleScraperContract(Protocol):
    """Minimal contract for single-article scrapers.

    Required API:
    - ``extract_by_url(url)`` as entrypoint;
    - ``_assemble_record(...)`` as domain composition hook.

    Extension rules:
    - payload hooks should be extended through
      ``_build_infobox_payload/_build_tables_payload/_build_sections_payload``;
    - ``extract_by_url`` signature must remain stable.
    """

    def extract_by_url(self, url: str) -> list[dict[str, Any]]: ...

    def _assemble_record(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class SectionParserContract(Protocol):
    """Minimal contract for section parser family.

    Required API:
    - ``parse(fragment)`` returning section parse payload.

    Extension rules:
    - parser variants may introduce extra helpers, but the ``parse`` entrypoint
      remains mandatory and should accept a soup/fragment object.
    """

    def parse(self, fragment: BeautifulSoup) -> SectionParseResult: ...


__all__ = [
    "ListScraperContract",
    "TableScraperContract",
    "SingleArticleScraperContract",
    "SectionParserContract",
]
