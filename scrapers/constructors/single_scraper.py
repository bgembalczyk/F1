from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.single_wiki_article import InfoboxPayloadDTO
from scrapers.base.single_wiki_article import SectionsPayloadDTO
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.base.single_wiki_article import TablesPayloadDTO
from scrapers.constructors.composition import ConstructorScraperCompositionFactory
from scrapers.constructors.composition import ConstructorScraperDependencies
from scrapers.constructors.postprocess.contract import (
    ConstructorSectionContractPostProcessor,
)
from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.postprocess.assembler import ConstructorRecordDTO

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions


class SingleConstructorScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        dependencies: ConstructorScraperDependencies | None = None,
        composition_factory: ConstructorScraperCompositionFactory | None = None,
    ) -> None:
        super().__init__(options=options)
        resolved_dependencies = dependencies
        if resolved_dependencies is None:
            resolved_dependencies = (
                composition_factory or ConstructorScraperCompositionFactory()
            ).build(options=self._options)

        self._infobox_service = resolved_dependencies.infobox_service
        self._sections_service_factory = resolved_dependencies.sections_service_factory
        self._domain_record_service = resolved_dependencies.domain_record_service

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        infoboxes = self._infobox_service.extract(soup, url=self.url).as_list()
        return InfoboxPayloadDTO(infoboxes)

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        return TablesPayloadDTO(self._domain_record_service.extract_tables(soup))

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        sections_service = self._sections_service_factory.create(
            adapter=self,
            options=self._options,
            url=self.url,
        )
        return SectionsPayloadDTO(sections_service.extract(soup))

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        _ = soup
        return self._domain_record_service.assemble_record(
            url=self.url,
            infoboxes=infobox_payload.data,
            tables=tables_payload.data,
            sections=sections_payload.data,
        )
