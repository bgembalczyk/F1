from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.base.single_wiki_article import InfoboxPayloadDTO
from scrapers.base.single_wiki_article import SectionsPayloadDTO
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.base.single_wiki_article import TablesPayloadDTO
from scrapers.drivers.domain_record_service import DomainRecordService
from scrapers.drivers.infobox.service import DriverInfoboxExtractionService
from scrapers.drivers.postprocess.contract import DriverSectionContractPostProcessor
from scrapers.drivers.sections.service import DriverSectionExtractionService

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory
    from scrapers.drivers.postprocess.assembler import DriverRecordAssembler


class DriverSectionServiceFactory(
    ValidatingSectionServiceFactory[DriverSectionExtractionService],
):
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: str | None = None,
    ) -> DriverSectionExtractionService:
        self._validate_dependencies(
            adapter=adapter,
            options=options,
            url=url,
            require_options=True,
            require_url=True,
        )
        return DriverSectionExtractionService(
            adapter=adapter,
            options=options,
            url=url,
        )


class SingleDriverScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        infobox_service: InfoboxExtractionService | None = None,
        sections_service_factory: (
            SectionServiceFactory[DriverSectionExtractionService] | None
        ) = None,
        assembler: DriverRecordAssembler | None = None,
        domain_record_service: DomainRecordService | None = None,
    ) -> None:
        super().__init__(options=options)
        self._infobox_service = infobox_service or DriverInfoboxExtractionService(
            options=self._options,
        )
        self._sections_service_factory = (
            sections_service_factory or DriverSectionServiceFactory()
        )
        self._domain_record_service = domain_record_service or DomainRecordService(
            assembler=assembler,
        )

    def _build_post_processor(self) -> DriverSectionContractPostProcessor:
        return DriverSectionContractPostProcessor()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        return InfoboxPayloadDTO(
            self._infobox_service.extract(soup, url=self.url).primary_record,
        )

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        records = self._sections_service_factory.create(
            adapter=self,
            options=self._options,
            url=self.url,
        ).extract(soup)
        return SectionsPayloadDTO(records)

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, object]:
        _ = soup, tables_payload
        return self._domain_record_service.assemble_record(
            url=self.url,
            infobox=infobox_payload.data,
            career_results=sections_payload.data,
        )
