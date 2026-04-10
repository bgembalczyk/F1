from typing import Any
from typing import Iterable

from bs4 import BeautifulSoup

from scrapers.base.infobox.extraction.result import InfoboxExtractionResult
from scrapers.base.infobox.extraction.result import ParserInputT
from scrapers.infobox.extraction.service.contracts import BaseInfoboxExtractionService
from scrapers.base.options import ScraperOptions
from scrapers.base.parsers.soup import SoupParser
from scrapers.extractors.infobox import InfoboxExtractor


class StrategyInfoboxExtractionService(BaseInfoboxExtractionService[ParserInputT]):
    """Adapter wykorzystujący strategię `InfoboxExtractor`."""

    def __init__(
        self,
        *,
        extractor: InfoboxExtractor[ParserInputT],
        options: ScraperOptions | None = None,
    ) -> None:
        super().__init__(options=options)
        self._extractor = extractor

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[ParserInputT]:
        return self._extractor.find_infoboxes(soup)

    def build_parser(self, *, url: str) -> SoupParser:
        return self._extractor.build_parser(options=self._options, url=url)

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult:
        return self._extractor.normalize_result(parsed_records)
