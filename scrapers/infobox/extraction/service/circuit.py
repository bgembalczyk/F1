from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.extractor import CircuitInfoboxExtractor
from scrapers.infobox.extraction.extractor import InfoboxExtractorProtocol
from scrapers.infobox.extraction.service.strategy import (
    StrategyBackedInfoboxExtractionService,
)

if TYPE_CHECKING:
    from scrapers.options import ScraperOptions


class CircuitInfoboxExtractionService(
    StrategyBackedInfoboxExtractionService[BeautifulSoup],
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
