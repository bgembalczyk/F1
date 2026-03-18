from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.constructors.infobox.service import ConstructorInfoboxExtractionService
from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.postprocess.contract import (
    ConstructorSectionContractPostProcessor,
)
from scrapers.constructors.sections.service import ConstructorSectionExtractionService
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from collections.abc import Callable

    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter


class SingleConstructorScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        infobox_service: ConstructorInfoboxExtractionService | None = None,
        sections_service_factory: (
            Callable[[SectionAdapter], ConstructorSectionExtractionService] | None
        ) = None,
        assembler: ConstructorRecordAssembler | None = None,
    ) -> None:
        super().__init__(options=options)
        self._infobox_service = infobox_service or ConstructorInfoboxExtractionService()
        self._sections_service_factory = sections_service_factory or (
            lambda adapter: ConstructorSectionExtractionService(adapter=adapter)
        )
        self._assembler = assembler or ConstructorRecordAssembler()
        self.article_tables_parser = ArticleTablesParser()

    def _build_post_processor(self) -> ConstructorSectionContractPostProcessor:
        return ConstructorSectionContractPostProcessor()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._infobox_service.extract(soup)

    def _build_tables_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self.article_tables_parser.parse(soup)

    def _build_sections_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        sections_service = self._sections_service_factory(self)
        return sections_service.extract(soup)

    def _scrape_infoboxes(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._build_infobox_payload(soup)

    def _scrape_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._build_tables_payload(soup)

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: list[dict[str, Any]],
        tables_payload: list[dict[str, Any]],
        sections_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        _ = soup
        return self._assembler.assemble(
            url=self.url,
            infoboxes=infobox_payload,
            tables=tables_payload,
            sections=sections_payload,
        )
