from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.constructors.contracts import ConstructorInfoboxExtractionServiceProtocol
from scrapers.constructors.contracts import ConstructorRecordAssemblerProtocol
from scrapers.constructors.contracts import ConstructorSectionExtractionServiceProtocol
from scrapers.constructors.infobox.service import ConstructorInfoboxExtractionService
from scrapers.constructors.postprocess import ConstructorSectionContractPostProcessor
from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.sections.service import ConstructorSectionExtractionService
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser
from scrapers.wiki.scraper import WikiScraper


class SingleConstructorScraper(SectionAdapter, WikiScraper):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        infobox_service: ConstructorInfoboxExtractionServiceProtocol | None = None,
        sections_service_factory: (
            Callable[[SectionAdapter], ConstructorSectionExtractionServiceProtocol] | None
        ) = None,
        assembler: ConstructorRecordAssemblerProtocol | None = None,
        article_tables_parser: ArticleTablesParser | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        options.post_processors.append(ConstructorSectionContractPostProcessor())
        super().__init__(options=options)
        self.url: str = ""
        self._infobox_service = infobox_service or ConstructorInfoboxExtractionService()
        self._sections_service_factory = (
            sections_service_factory
            or (lambda adapter: ConstructorSectionExtractionService(adapter=adapter))
        )
        self._assembler = assembler or ConstructorRecordAssembler()
        self.article_tables_parser = article_tables_parser or ArticleTablesParser()

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _scrape_infoboxes(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._infobox_service.extract(soup)

    def _scrape_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self.article_tables_parser.parse(soup)

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        sections_service = self._sections_service_factory(self)
        return [
            self._assembler.assemble(
                url=self.url,
                infoboxes=self._scrape_infoboxes(soup),
                tables=self._scrape_tables(soup),
                sections=sections_service.extract(soup),
            ),
        ]
