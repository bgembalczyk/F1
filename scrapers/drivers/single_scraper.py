from __future__ import annotations

from typing import TYPE_CHECKING

from models.value_objects import SectionId
from scrapers.base.single_wiki_article.dto import InfoboxPayloadDTO
from scrapers.base.single_wiki_article.dto import SectionsPayloadDTO
from scrapers.base.single_wiki_article.dto import TablesPayloadDTO
from scrapers.base.single_wiki_article.section_adapter import (
    SingleWikiArticleSectionAdapterBase,
)
from scrapers.drivers.composition import DriverScraperCompositionFactory
from scrapers.drivers.composition import DriverScraperDependencies

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions


class SingleDriverScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        dependencies: DriverScraperDependencies | None = None,
        composition_factory: DriverScraperCompositionFactory | None = None,
    ) -> None:
        super().__init__(options=options)
        resolved_dependencies = dependencies
        if resolved_dependencies is None:
            resolved_dependencies = (
                composition_factory or DriverScraperCompositionFactory()
            ).build(options=self._options)

        self._infobox_service = resolved_dependencies.infobox_service
        self._sections_service_factory = resolved_dependencies.sections_service_factory
        self._domain_record_service = resolved_dependencies.domain_record_service

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
        normalized_records = [
            {
                **record,
                "section_id": SectionId.from_raw(str(record.get("section_id", ""))).to_export()
                if record.get("section_id")
                else record.get("section_id"),
            }
            if isinstance(record, dict)
            else record
            for record in records
        ]
        return SectionsPayloadDTO(normalized_records)

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
