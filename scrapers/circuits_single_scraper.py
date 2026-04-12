from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.circuits_composition import CircuitScraperCompositionFactory
from scrapers.circuits_composition import CircuitScraperDependencies
from scrapers.dto import InfoboxPayloadDTO
from scrapers.dto import SectionsPayloadDTO
from scrapers.dto import TablesPayloadDTO
from scrapers.helpers.sections import is_circuit_like_article
from scrapers.section.selection_strategy.wikipedia_by_id import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.services.domain_record.circuit_lap_records_extraction_service import (
    CircuitLapRecordsExtractionService,
)
from scrapers.services.domain_record.circuit_pipeline_service import (
    CircuitDomainRecordInput,
)
from scrapers.single_wiki_article import SectionAdapterScraperBase

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.options import ScraperOptions


class F1SingleCircuitScraper(SectionAdapterScraperBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        dependencies: CircuitScraperDependencies | None = None,
        composition_factory: CircuitScraperCompositionFactory | None = None,
    ) -> None:
        super().__init__(
            options=options,
            section_selection_strategy=WikipediaSectionByIdSelectionStrategy(
                domain="circuits",
            ),
        )
        resolved_dependencies = dependencies
        if resolved_dependencies is None:
            resolved_dependencies = (
                composition_factory or CircuitScraperCompositionFactory()
            ).build(options=self._options)

        self._infobox_service = resolved_dependencies.infobox_service
        self._sections_service_factory = resolved_dependencies.sections_service_factory
        self._domain_record_service = resolved_dependencies.domain_record_service
        self._lap_records_extraction_service = CircuitLapRecordsExtractionService()

    def _is_circuit_like_article(self, soup: BeautifulSoup) -> bool:
        return is_circuit_like_article(soup)

    def _should_parse_article(self, soup: BeautifulSoup) -> bool:
        return self._is_circuit_like_article(soup)

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
            self._lap_records_extraction_service.collect_lap_record_rows(
                soup=soup,
                url=self.url,
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                policy=self.policy,
                debug_dir=self.debug_dir,
            ),
        )

    def _build_sections_payload(
        self,
        soup: BeautifulSoup,
    ) -> SectionsPayloadDTO:
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
        details_record = self.parse_details(soup)
        if details_record is not None:
            record = details_record
            return {"url": self._original_url or self.url, **record}

        return self._domain_record_service.assemble_record(
            CircuitDomainRecordInput(
                source_url=self._original_url or self.url,
                infobox=infobox_payload.data,
                lap_record_rows=tables_payload.data,
                sections=sections_payload.data,
            ),
        )

    def parse_details(self, soup: BeautifulSoup) -> dict[str, Any] | None:
        if type(self)._parse_details is F1SingleCircuitScraper._parse_details:  # noqa: SLF001
            return None
        return self._parse_details(soup)

    def _parse_details(self, soup: BeautifulSoup) -> dict[str, Any]:
        _ = soup
        return {}
