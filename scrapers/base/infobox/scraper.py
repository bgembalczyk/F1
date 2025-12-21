from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup

from infrastructure.http_client.interfaces import HttpClientProtocol
from infrastructure.http_client.policies import ResponseCache
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import build_http_config
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
        user_agent: str | None = None,
        timeout: int = 10,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        retries: int = 0,
        http_client: Optional[HttpClientProtocol] = None,
        cache: ResponseCache | None = None,
        fetcher: HtmlFetcher | None = None,
        parser: InfoboxHtmlParser | None = None,
        mapper: InfoboxFieldMapper | None = None,
    ) -> None:
        if fetcher is None:
            fetcher = HtmlFetcher(
                config=build_http_config(
                    session=session,
                    headers=headers,
                    user_agent=user_agent,
                    timeout=timeout,
                    retries=retries,
                    cache=cache,
                    http_client=http_client,
                ),
            )

        self.fetcher = fetcher
        self.timeout = timeout
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
