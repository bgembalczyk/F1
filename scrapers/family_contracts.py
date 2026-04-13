from __future__ import annotations

from typing import Any
from typing import Protocol
from typing import runtime_checkable


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


__all__ = [
    "SingleArticleScraperContract",
]
