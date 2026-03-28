from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.drivers.infobox.service import DriverInfoboxExtractionService
from scrapers.drivers.postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.postprocess.contract import DriverSectionContractPostProcessor
from scrapers.drivers.sections.service import DriverSectionExtractionService

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory


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
    ) -> None:
        super().__init__(options=options)
        self._infobox_service = infobox_service or DriverInfoboxExtractionService(
            options=self._options,
        )
        self._sections_service_factory = (
            sections_service_factory or DriverSectionServiceFactory()
        )
        self._assembler = assembler or DriverRecordAssembler()

    def _build_post_processor(self) -> DriverSectionContractPostProcessor:
        return DriverSectionContractPostProcessor()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> dict[str, Any]:
        return self._infobox_service.extract(soup, url=self.url).primary_record

    def _build_sections_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self._sections_service_factory.create(
            adapter=self,
            options=self._options,
            url=self.url,
        ).extract(soup)

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: dict[str, Any],
        tables_payload: list[dict[str, Any]],
        sections_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        _ = soup, tables_payload
        return self._assembler.assemble(
            url=self.url,
            infobox=infobox_payload,
            career_results=sections_payload,
        )
