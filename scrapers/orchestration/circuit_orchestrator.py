from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.extractor import CircuitInfoboxExtractor
from scrapers.infobox.extraction.result import InfoboxExtractionResult
from scrapers.options import ScraperOptions
from scrapers.orchestration.base_infobox_orchestrator import BaseInfoboxOrchestrator
from scrapers.parsers.soup import SoupParser
from scrapers.protocols.infobox_extractor import InfoboxExtractorABC

if TYPE_CHECKING:
    from collections.abc import Iterable


class CircuitInfoboxOrchestrator(BaseInfoboxOrchestrator[BeautifulSoup]):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        strategy: InfoboxExtractorABC[BeautifulSoup] | None = None,
    ) -> None:
        super().__init__(options=options)
        self._strategy = strategy or CircuitInfoboxExtractor()

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[BeautifulSoup]:
        return self._strategy.find_infoboxes(soup)

    def build_parser(self, *, url: str) -> SoupParser:
        return self._strategy.build_parser(options=self._options, url=url)

    def normalize_result(
        self,
        parsed_records: list[dict[str, object]],
    ) -> InfoboxExtractionResult:
        return self._strategy.normalize_result(parsed_records)
