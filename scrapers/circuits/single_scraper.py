from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.base.single_wiki_article import InfoboxPayloadDTO
from scrapers.base.single_wiki_article import SectionsPayloadDTO
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.base.single_wiki_article import TablesPayloadDTO
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.circuits.helpers.article_validation import is_circuit_like_article
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.lap_record import is_lap_record_table
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.circuits.infobox.service import CircuitInfoboxExtractionService
from scrapers.circuits.postprocess.assembler import CircuitRecordAssembler
from scrapers.circuits.postprocess.assembler import CircuitRecordDTO
from scrapers.circuits.sections.service import CircuitSectionExtractionService
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.infobox.service import InfoboxExtractionService
    from scrapers.base.sections.adapter import SectionAdapter
    from scrapers.base.sections.interface import SectionServiceFactory


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
    ) -> None:
        super().__init__(
            options=options,
            section_selection_strategy=WikipediaSectionByIdSelectionStrategy(
                domain="circuits",
            ),
        )
        self.article_tables_parser = ArticleTablesParser(include_source_table=True)
        self._infobox_service = infobox_service or CircuitInfoboxExtractionService(
            options=self._options,
        )
        self._sections_service_factory = (
            sections_service_factory or CircuitSectionServiceFactory()
        )
        self._assembler = assembler or CircuitRecordAssembler()

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
        lap_scraper = LapRecordsTableScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                policy=self.policy,
                debug_dir=self.debug_dir,
            ),
        )
        lap_scraper.url = self.url
        all_records: list[dict[str, Any]] = []

        for table_data in self.article_tables_parser.parse(soup):
            table = table_data.get("_table")
            if table is None:
                continue

            headers = table_data["headers"]
            table_type = table_data.get("table_type")
            if table_type != "lap_records" and not is_lap_record_table(
                headers,
                lap_scraper,
            ):
                continue

            base_layout = detect_layout_name(table, headers)
            all_records.extend(
                collect_lap_records(table, headers, base_layout, lap_scraper),
            )

        return TablesPayloadDTO(all_records)

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
        return self._assembler.assemble(
            payload=CircuitRecordDTO(
                url=self._original_url or self.url,
                infobox=infobox_payload.data,
                lap_record_rows=tables_payload.data,
                sections=sections_payload.data,
            ),
        )
