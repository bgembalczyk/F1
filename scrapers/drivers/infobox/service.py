from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.drivers.infobox.scraper import DriverInfoboxParser


class DriverInfoboxExtractionService:
    def __init__(
        self,
        *,
        include_urls: bool,
        debug_dir: str | None,
        run_id: str | None,
    ) -> None:
        self._include_urls = include_urls
        self._debug_dir = debug_dir
        self._run_id = run_id

    def extract(self, soup: BeautifulSoup, *, url: str) -> dict[str, Any]:
        table = soup.find("table", class_="infobox")
        if table is None:
            return {}

        parser = DriverInfoboxParser(
            options=ScraperOptions(
                include_urls=self._include_urls,
                debug_dir=self._debug_dir,
            ),
            run_id=self._run_id,
            url=url,
        )
        records = parser.parse(table)
        return records[0] if records else {}
