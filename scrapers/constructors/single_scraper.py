from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.base.single_wiki_article import InfoboxPayloadDTO
from scrapers.base.single_wiki_article import SectionsPayloadDTO
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.base.single_wiki_article import TablesPayloadDTO
from scrapers.constructors.domain_record_service import DomainRecordService
from scrapers.constructors.infobox.service import ConstructorInfoboxExtractionService
from scrapers.constructors.postprocess.contract import (
    ConstructorSectionContractPostProcessor,
)
from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.postprocess.assembler import ConstructorRecordDTO
from scrapers.constructors.sections.service import ConstructorSectionExtractionService

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory
    from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler


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
        domain_record_service: DomainRecordService | None = None,
    ) -> None:
        super().__init__(options=options)
        self._infobox_service = infobox_service or ConstructorInfoboxExtractionService(
            options=self._options,
        )
        self._sections_service_factory = (
            sections_service_factory or ConstructorSectionServiceFactory()
        )
        self._domain_record_service = domain_record_service or DomainRecordService(
            assembler=assembler,
        )

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
