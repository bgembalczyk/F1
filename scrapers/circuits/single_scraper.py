from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.factory import ValidatingSectionServiceFactory
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.circuits.helpers.article_validation import is_circuit_like_article
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.lap_record import is_lap_record_table
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.circuits.infobox.service import CircuitInfoboxExtractionService
from scrapers.circuits.postprocess.assembler import CircuitRecordAssembler
from scrapers.circuits.postprocess.contract import CircuitSectionContractPostProcessor
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
        super().__init__(options=options, section_selection_domain="circuits")
        self.article_tables_parser = ArticleTablesParser(include_source_table=True)
        self._infobox_service = infobox_service or CircuitInfoboxExtractionService(
            options=self._options,
        )
        self._sections_service_factory = (
            sections_service_factory or CircuitSectionServiceFactory()
        )
        self._assembler = assembler or CircuitRecordAssembler()

    def _build_post_processor(self) -> CircuitSectionContractPostProcessor:
        return CircuitSectionContractPostProcessor()

    def _uses_url_fragment(self) -> bool:
        return True

    def _should_parse_article(self, soup: BeautifulSoup) -> bool:
        return is_circuit_like_article(soup)

    def _build_infobox_payload(self, soup: BeautifulSoup) -> dict[str, Any]:
        return self._infobox_service.extract(soup, url=self.url).primary_record

    def _build_tables_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
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

        layouts: dict[str, list[dict[str, Any]]] = {}
        for rec in all_records:
            layout_name = rec.get("layout")
            if not layout_name:
                continue

            rec_copy = dict(rec)
            rec_copy.pop("layout", None)
            layouts.setdefault(layout_name, []).append(rec_copy)

        return [
            {"layout": layout_name, "lap_records": recs}
            for layout_name, recs in layouts.items()
        ]

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
        infobox_payload: dict[str, Any],
        tables_payload: list[dict[str, Any]],
        sections_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        _ = soup
        return self._assembler.assemble(
            url=self._original_url or self.url,
            infobox=infobox_payload,
            tables=tables_payload,
            sections=sections_payload,
        )
