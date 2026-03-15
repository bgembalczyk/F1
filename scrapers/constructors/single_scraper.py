from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.options import ScraperOptions
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser
from scrapers.wiki.scraper import WikiScraper


class SingleConstructorScraper(WikiScraper):
    """
    Scraper pojedynczego konstruktora - pobiera wszystkie infoboksy
    oraz wszystkie tabele z artykułu Wikipedii.
    """

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self.url: str = ""
        self.article_tables_parser = ArticleTablesParser()

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [
            {
                "url": self.url,
                "infoboxes": self._scrape_infoboxes(soup),
                "tables": self._scrape_tables(soup),
            },
        ]

    def _scrape_infoboxes(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = InfoboxHtmlParser()
        return [parser.parse_element(table) for table in self.find_infoboxes(soup)]

    def _scrape_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self.article_tables_parser.parse(soup)
