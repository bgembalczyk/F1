from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from typing import Any
from typing import Generic

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.result import InfoboxExtractionResult
from scrapers.infobox.extraction.result import ParserInputT
from scrapers.options import ScraperOptions
from scrapers.parsers.soup import SoupParser


class InfoboxExtractorABC(ABC, Generic[ParserInputT]):
    """Kontrakt strategii ekstrakcji infoboxów dla konkretnej domeny."""

    @abstractmethod
    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[ParserInputT]: ...

    @abstractmethod
    def build_parser(
        self,
        *,
        options: ScraperOptions,
        url: str,
    ) -> SoupParser: ...

    @abstractmethod
    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult: ...


__all__ = ["InfoboxExtractorABC"]
