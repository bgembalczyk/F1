from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.base.infobox.extraction.result import InfoboxExtractionResult


class InfoboxExtractionService(Protocol):
    """Wspólne API wymagane przez scrapery domenowe."""

    def extract(
        self,
        soup: BeautifulSoup,
        *,
        url: str = "",
    ) -> InfoboxExtractionResult: ...
