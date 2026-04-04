from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.single_wiki_article.dto import InfoboxPayloadDTO
from scrapers.base.single_wiki_article.dto import SectionsPayloadDTO
from scrapers.base.single_wiki_article.dto import TablesPayloadDTO
from scrapers.base.single_wiki_article.section_adapter import (
    SingleWikiArticleSectionAdapterBase,
)
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.circuits.composition import CircuitScraperCompositionFactory
from scrapers.circuits.composition import CircuitScraperDependencies
from scrapers.circuits.helpers.lap_record import is_lap_record_table
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.circuits.helpers.sections import is_circuit_like_article

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions

__all__ = [
    "F1SingleCircuitScraper",
    "detect_layout_name",
    "is_lap_record_table",
]


class F1SingleCircuitScraper(SingleWikiArticleSectionAdapterBase):
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
