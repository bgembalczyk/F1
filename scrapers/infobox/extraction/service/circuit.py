from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.extractor.circuit import CircuitInfoboxExtractionStrategy
from scrapers.infobox.extraction.extractor.protocol import InfoboxExtractionStrategy
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
        strategy: InfoboxExtractionStrategy[BeautifulSoup] | None = None,
    ) -> None:
        super().__init__(
            strategy=strategy or CircuitInfoboxExtractionStrategy(),
            options=options,
        )
