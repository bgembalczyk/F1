from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.constructors.infobox.service import ConstructorInfoboxExtractionService
from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.postprocess.contract import (
    ConstructorSectionContractPostProcessor,
)
from scrapers.constructors.sections.service import ConstructorSectionExtractionService
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory


class ConstructorSectionServiceFactory(
    ValidatingSectionServiceFactory[ConstructorSectionExtractionService],
):
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: str | None = None,
    ) -> ConstructorSectionExtractionService:
        self._validate_dependencies(
            adapter=adapter,
            options=options,
            url=url,
            require_options=True,
            require_url=True,
        )
        return ConstructorSectionExtractionService(
            adapter=adapter,
            options=options,
            url=url,
        )


class SingleConstructorScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        infobox_service: InfoboxExtractionService | None = None,
        sections_service_factory: (
            SectionServiceFactory[ConstructorSectionExtractionService] | None
        ) = None,
        assembler: ConstructorRecordAssembler | None = None,
    ) -> None:
        super().__init__(options=options)
        self._infobox_service = infobox_service or ConstructorInfoboxExtractionService(
            options=self._options,
        )
        self._sections_service_factory = (
            sections_service_factory or ConstructorSectionServiceFactory()
        )
        self._assembler = assembler or ConstructorRecordAssembler()
        self.article_tables_parser = ArticleTablesParser()

    def _build_post_processor(self) -> ConstructorSectionContractPostProcessor:
        return ConstructorSectionContractPostProcessor()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._infobox_service.extract(soup, url=self.url).as_list()

    def _build_tables_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self.article_tables_parser.parse(soup)

    def _build_sections_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        sections_service = self._sections_service_factory.create(
            adapter=self,
            options=self._options,
            url=self.url,
        )
        return sections_service.extract(soup)

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
