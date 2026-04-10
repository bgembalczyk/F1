from collections.abc import Iterable
from typing import Any
from typing import Generic
from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.result import InfoboxExtractionResult
from scrapers.infobox.extraction.result import ParserInputT
from scrapers.options import ScraperOptions
from scrapers.parsers.soup import SoupParser


class InfoboxExtractorProtocol(Protocol, Generic[ParserInputT]):
    """Kontrakt strategii ekstrakcji infoboxów dla konkretnej domeny."""

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[ParserInputT]: ...

    def build_parser(
        self,
        *,
        options: ScraperOptions,
        url: str,
    ) -> SoupParser: ...

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult: ...


InfoboxExtractionStrategy = InfoboxExtractorProtocol
