from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.base.single_wiki_article import InfoboxPayloadDTO
from scrapers.base.single_wiki_article import SectionsPayloadDTO
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.base.single_wiki_article import TablesPayloadDTO
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.circuits.domain_record_service import DomainRecordService
from scrapers.circuits.helpers.article_validation import is_circuit_like_article
from scrapers.circuits.helpers.lap_record import (
    is_lap_record_table as _is_lap_record_table,
)
from scrapers.circuits.helpers.layout import detect_layout_name as _detect_layout_name
from scrapers.circuits.infobox.service import CircuitInfoboxExtractionService
from scrapers.circuits.postprocess.contract import CircuitSectionContractPostProcessor
from scrapers.circuits.sections.service import CircuitSectionExtractionService

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory
    from scrapers.circuits.postprocess.assembler import CircuitRecordAssembler

is_lap_record_table = _is_lap_record_table
detect_layout_name = _detect_layout_name


class CircuitSectionServiceFactory(
    ValidatingSectionServiceFactory[CircuitSectionExtractionService],
):
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: str | None = None,
    ) -> CircuitSectionExtractionService:
        self._validate_dependencies(
            adapter=adapter,
            options=options,
            url=url,
            require_options=True,
            require_url=True,
        )
        return CircuitSectionExtractionService(
            adapter=adapter,
            options=options,
            url=url,
        )


class F1SingleCircuitScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        infobox_service: InfoboxExtractionService | None = None,
        sections_service_factory: (
            SectionServiceFactory[CircuitSectionExtractionService] | None
        ) = None,
        assembler: CircuitRecordAssembler | None = None,
        domain_record_service: DomainRecordService | None = None,
    ) -> None:
        super().__init__(
            options=options,
            section_selection_strategy=WikipediaSectionByIdSelectionStrategy(
                domain="circuits",
            ),
        )
        self._infobox_service = infobox_service or CircuitInfoboxExtractionService(
            options=self._options,
        )
        self._sections_service_factory = (
            sections_service_factory or CircuitSectionServiceFactory()
        )
        self._domain_record_service = domain_record_service or DomainRecordService(
            assembler=assembler,
        )

    def _build_post_processor(self) -> CircuitSectionContractPostProcessor:
        return CircuitSectionContractPostProcessor()

    def _should_parse_article(self, soup: BeautifulSoup) -> bool:
        return is_circuit_like_article(soup)

    def _select_section(
        self,
        soup: BeautifulSoup,
        fragment: str | None,
    ) -> BeautifulSoup:
        if not fragment:
            return soup

        section = self.extract_section_by_id(soup, fragment, domain="circuits")
        return section or soup

    def _prepare_article_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        return self._select_section(soup, self._section_fragment)

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        return InfoboxPayloadDTO(
            self._infobox_service.extract(soup, url=self.url).primary_record,
        )

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        return TablesPayloadDTO(
            self._domain_record_service.collect_lap_record_rows(
                soup=soup,
                url=self.url,
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                policy=self.policy,
                debug_dir=self.debug_dir,
            ),
        )

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
            source_url=self._original_url or self.url,
            infobox=infobox_payload.data,
            lap_record_rows=tables_payload.data,
            sections=sections_payload.data,
        )
