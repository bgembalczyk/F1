from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Generic

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.extractor import CircuitInfoboxExtractor
from scrapers.infobox.extraction.mixins import ParsedRecordsMixin
from scrapers.infobox.extraction.result import InfoboxExtractionResult
from scrapers.infobox.extraction.result import ParserInputT
from scrapers.options import ScraperOptions
from scrapers.orchestration.infobox_orchestrator_abc import InfoboxOrchestratorABC
from scrapers.protocols.infobox_extractor import InfoboxExtractorABC


class CircuitInfoboxOrchestrator(
    InfoboxOrchestratorABC,
    ParsedRecordsMixin,
    Generic[ParserInputT],
):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        strategy: InfoboxExtractorABC[BeautifulSoup] | None = None,
    ) -> None:
        self._strategy = strategy or CircuitInfoboxExtractor()
        self._options = options or ScraperOptions()

    def extract(
        self,
        soup: BeautifulSoup,
        *,
        url: str = "",
    ) -> InfoboxExtractionResult:
        parser = self._strategy.build_parser(options=self._options, url=url)
        parsed_records: list[dict[str, object]] = []
        for infobox in self._strategy.find_infoboxes(soup):
            parsed_records.extend(self.coerce_records(parser.parse(infobox)))
        return self._strategy.normalize_result(parsed_records)
