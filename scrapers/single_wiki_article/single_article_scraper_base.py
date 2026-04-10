from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

from infrastructure.helpers import init_scraper_options
from scrapers.helpers.config_factory import build_scraper_options
from scrapers.runtime.factory import ScraperRuntimeFactory
from scrapers.wiki.scraper_wiki import WikiScraper

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.options import ScraperOptions


class SingleArticleScraperBase(WikiScraper, ABC):
    """Baza odpowiedzialna za fetch i lifecycle pojedynczego artykułu."""

    options_domain: str | None = None
    options_profile: str = "article_strict"

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        include_urls: bool = True,
    ) -> None:
        resolved_options = init_scraper_options(options, include_urls=include_urls)
        resolved_options = build_scraper_options(
            domain=self.options_domain,
            profile=self.options_profile,
            options=resolved_options,
            scraper_cls=type(self),
        )
        policy = self.get_http_policy(resolved_options)
        runtime = ScraperRuntimeFactory().build(options=resolved_options, policy=policy)
        resolved_options.fetcher = runtime.fetcher
        resolved_options.source_adapter = runtime.source_adapter

        super().__init__(options=resolved_options)
        self.url: str = ""
        self._original_url: str | None = None
        self._options = resolved_options
        self.policy = self.http_policy
        self.debug_dir = resolved_options.debug_dir

    def extract_by_url(self, url: str) -> list[dict[str, Any]]:
        self._original_url = url
        self.url = url
        return super().fetch()

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if not self._should_parse_article(soup):
            return []

        working_soup = self._prepare_article_soup(soup)
        if self.parser is not None:
            return self.parser.parse(working_soup)
        return self._parse_soup(working_soup)

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [self._build_article_record(soup)]

    def _should_parse_article(self, soup: BeautifulSoup) -> bool:
        _ = soup
        return True

    def _prepare_article_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        return soup

    @abstractmethod
    def _build_article_record(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Build final record from parsed article soup."""


__all__ = ["SingleArticleScraperBase"]
