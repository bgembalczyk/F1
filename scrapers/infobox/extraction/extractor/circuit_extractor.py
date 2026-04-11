from collections.abc import Iterable
from typing import Any

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.result import InfoboxExtractionResult
from scrapers.options import ScraperOptions
from scrapers.parsers.infobox.circuit import F1CircuitInfoboxParser
from scrapers.parsers.soup import SoupParser
from scrapers.protocols.infobox_extractor import InfoboxExtractorProtocol


class CircuitInfoboxExtractor(InfoboxExtractorProtocol[BeautifulSoup]):
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


__all__ = ["CircuitInfoboxExtractor"]
