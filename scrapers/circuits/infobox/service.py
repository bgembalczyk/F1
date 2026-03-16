from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.circuits.infobox.scraper import F1CircuitInfoboxParser


class CircuitInfoboxExtractionService:
    def __init__(self, *, include_urls: bool, debug_dir: str | None) -> None:
        self._include_urls = include_urls
        self._debug_dir = debug_dir

    def extract(self, soup: BeautifulSoup, *, url: str) -> dict[str, Any]:
        parser = F1CircuitInfoboxParser(
            options=ScraperOptions(
                include_urls=self._include_urls,
                debug_dir=self._debug_dir,
            ),
            url=url,
        )
        records = parser.parse(soup)
        return records[0] if records else {}
