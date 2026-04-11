from collections.abc import Iterable
from typing import Any

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.result import InfoboxExtractionResult
from scrapers.infobox.extraction.result import ParserInputT
from scrapers.infobox.extraction.service.base_infobox_orchestrator import BaseInfoboxOrchestrator
from scrapers.options import ScraperOptions
from scrapers.parsers.soup import SoupParser
from scrapers.protocols.infobox_extractor import InfoboxExtractorProtocol


class StrategyBackedInfoboxOrchestrator(
    BaseInfoboxOrchestrator[ParserInputT],
):
    """Adapter delegujący ekstrakcję do obiektu strategii."""

    def __init__(
        self,
        *,
        strategy: InfoboxExtractorProtocol[ParserInputT],
        options: ScraperOptions | None = None,
    ) -> None:
        super().__init__(options=options)
        self._strategy = strategy

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[ParserInputT]:
        return self._strategy.find_infoboxes(soup)

    def build_parser(self, *, url: str) -> SoupParser:
        return self._strategy.build_parser(options=self._options, url=url)

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult:
        return self._strategy.normalize_result(parsed_records)
