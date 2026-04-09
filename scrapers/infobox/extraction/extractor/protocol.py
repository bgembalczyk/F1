from typing import Any
from typing import Generic
from typing import Iterable
from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.base.infobox.extraction.result import InfoboxExtractionResult
from scrapers.base.infobox.extraction.result import ParserInputT
from scrapers.base.options import ScraperOptions
from scrapers.base.parsers.soup import SoupParser


class InfoboxExtractor(Protocol, Generic[ParserInputT]):
    """Strategia ekstrakcji infoboxów dla konkretnej domeny."""

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
