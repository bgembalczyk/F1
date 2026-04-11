from __future__ import annotations

from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.result import InfoboxExtractionResult


class InfoboxOrchestratorProtocol(Protocol):
    """Common API required by domain scrapers."""

    def extract(
        self,
        soup: BeautifulSoup,
        *,
        url: str = "",
    ) -> InfoboxExtractionResult: ...


InfoboxExtractionService = InfoboxOrchestratorProtocol

__all__ = [
    "InfoboxExtractionService",
    "InfoboxOrchestratorProtocol",
]
