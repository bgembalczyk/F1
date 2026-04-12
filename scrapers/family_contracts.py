from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable

if False:  # pragma: no cover
    from bs4 import BeautifulSoup


@runtime_checkable
class ListScraperContract(Protocol):
    """Minimal contract for list/seed scrapers.

    Extension rules:
    - Override _parse_soup to customise HTML→records parsing.
    """

    def fetch(self) -> list[dict[str, Any]]: ...


@runtime_checkable
class TableScraperContract(Protocol):
    """Minimal contract for table-based scrapers.

    Extension rules:
    - Override parse_soup to customise soup→records parsing.
    - Override parse_row to customise row→record mapping.
    - Override _parse_soup for lower-level soup access.
    """

    def parse_soup(self, soup: BeautifulSoup) -> list[Any]: ...

    def parse_row(self, row: Any) -> Any | None: ...


@runtime_checkable
class SingleArticleScraperContract(Protocol):
    """Minimal contract for single-article scrapers.

    Extension rules:
    - Override _assemble_record to customise the final record shape.
    - Override _build_infobox_payload to customise infobox extraction.
    - Override _build_tables_payload to customise table extraction.
    - Override _build_sections_payload to customise section extraction.
    - Override _before_payload_build for pre-build hooks.
    - Override _after_record_assembled for post-assembly hooks.
    - Override _should_parse_article to control whether parsing runs.
    - Override _prepare_article_soup to pre-process the soup.
    """

    def extract_by_url(self, url: str) -> list[dict[str, Any]]: ...

    def _assemble_record(self, **kwargs: Any) -> dict[str, Any]: ...


@runtime_checkable
class SectionParserContract(Protocol):
    """Minimal contract for section parsers.

    Extension rules:
    - Override parse to customise section parsing behaviour.
    """

    def parse(self, element: Any) -> Any: ...


__all__ = [
    "ListScraperContract",
    "TableScraperContract",
    "SingleArticleScraperContract",
    "SectionParserContract",
]
