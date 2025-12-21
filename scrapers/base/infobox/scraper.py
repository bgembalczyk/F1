from __future__ import annotations

from typing import Any, Dict
from bs4 import BeautifulSoup

import logging

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.errors import ScraperError
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import ScraperOptions
from scrapers.base.infobox.field_mapper import InfoboxFieldMapper
from scrapers.base.infobox.html_parser import InfoboxHtmlParser


class WikipediaInfoboxScraper:
    """
    Scraper infoboksów z artykułów Wikipedii.

    Użycie:
        scraper = WikipediaInfoboxScraper()
        data = scraper.scrape("https://en.wikipedia.org/wiki/Lewis_Hamilton")
    """

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        fetcher: HtmlFetcher | None = None,
        parser: InfoboxHtmlParser | None = None,
        mapper: InfoboxFieldMapper | None = None,
    ) -> None:
        options = options or ScraperOptions()
        if fetcher is not None:
            options.fetcher = fetcher

        self.fetcher = options.with_fetcher()
        self.timeout = options.to_http_config().timeout
        self.parser = parser or InfoboxHtmlParser()
        self.mapper = mapper or InfoboxFieldMapper()

    # ------------------------------
    # Public API
    # ------------------------------

    def scrape(self, url: str) -> Dict[str, Any]:
        """Pobiera i parsuje infobox z dowolnego artykułu Wikipedii."""
        handler = ErrorHandler(logger=logging.getLogger(__name__))
        try:
            html = self._fetch(url)
        except Exception as exc:
            error = exc if isinstance(exc, ScraperError) else handler.wrap_network(exc, url=url)
            if handler.handle(error):
                return {}
            if error is exc:
                raise
            raise error from exc

        try:
            soup = BeautifulSoup(html, "html.parser")
            return self.parse_from_soup(soup)
        except Exception as exc:
            error = exc if isinstance(exc, ScraperError) else handler.wrap_parse(exc, url=url)
            if handler.handle(error):
                return {}
            if error is exc:
                raise
            raise error from exc

    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parsuje infobox z już utworzonego obiektu ``BeautifulSoup``."""
        raw = self.parser.parse(soup)
        return self.mapper.map(raw)

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def _fetch(self, url: str) -> str:
        return self.fetcher.get_text(url, timeout=self.timeout)
