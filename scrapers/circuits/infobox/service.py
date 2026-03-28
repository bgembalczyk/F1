from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.infobox.service import InfoboxExtractionResult
from scrapers.base.infobox.service import InfoboxExtractor
from scrapers.base.infobox.service import StrategyInfoboxExtractionService
from scrapers.circuits.infobox.scraper import F1CircuitInfoboxParser

if TYPE_CHECKING:
    from collections.abc import Iterable

    from scrapers.base.options import ScraperOptions
    from scrapers.base.parsers.soup import SoupParser


class CircuitInfoboxExtractor(InfoboxExtractor[BeautifulSoup]):
    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[BeautifulSoup]:
        return [soup]

    def build_parser(self, *, options: ScraperOptions, url: str) -> SoupParser:
        return F1CircuitInfoboxParser(
            options=options,
            url=url,
        )

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult:
        return InfoboxExtractionResult(
            records=[dict(record) for record in parsed_records],
        )


class CircuitInfoboxExtractionService(StrategyInfoboxExtractionService[BeautifulSoup]):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        extractor: InfoboxExtractor[BeautifulSoup] | None = None,
    ) -> None:
        super().__init__(
            extractor=extractor or CircuitInfoboxExtractor(),
            options=options,
        )
