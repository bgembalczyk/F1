from __future__ import annotations

from typing import Any, Dict
from bs4 import BeautifulSoup

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
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        return self.parse_from_soup(soup)

    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parsuje infobox z już utworzonego obiektu ``BeautifulSoup``."""
        raw = self.parser.parse_from_soup(soup)
        return self.mapper.map(raw)

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def _fetch(self, url: str) -> str:
        return self.fetcher.get_text(url, timeout=self.timeout)
