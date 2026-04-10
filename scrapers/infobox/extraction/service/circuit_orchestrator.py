from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.extractor.circuit_extractor import CircuitInfoboxExtractor
from scrapers.infobox.extraction.extractor import InfoboxExtractorProtocol
from scrapers.infobox.extraction.service.strategy import (
    StrategyBackedInfoboxOrchestrator,
)

if TYPE_CHECKING:
    from scrapers.options import ScraperOptions


class CircuitInfoboxOrchestrator(
    StrategyBackedInfoboxOrchestrator[BeautifulSoup],
):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        strategy: InfoboxExtractorProtocol[BeautifulSoup] | None = None,
    ) -> None:
        super().__init__(
            strategy=strategy or CircuitInfoboxExtractor(),
            options=options,
        )
