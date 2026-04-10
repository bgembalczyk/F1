from __future__ import annotations

import warnings

warnings.warn("single_scraper_seasons is deprecated; use scrapers.seasons_detail_scraper.", DeprecationWarning, stacklevel=2)

from typing import TYPE_CHECKING
from typing import Any

from scrapers.seasons.composition_seasons import SeasonScraperCompositionFactory
from scrapers.seasons.composition_seasons import SeasonScraperDependencies
from scrapers.seasons.postprocess_seasons.assembler import SeasonPayloadDTO
from scrapers.services.domain_record.season import SeasonDomainRecordInput
from scrapers.single_wiki_article import InfoboxPayloadDTO
from scrapers.single_wiki_article import SectionsPayloadDTO
from scrapers.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.single_wiki_article import TablesPayloadDTO

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.options import ScraperOptions


class SingleSeasonScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        season_year: int | None = None,
        dependencies: SeasonScraperDependencies | None = None,
        composition_factory: SeasonScraperCompositionFactory | None = None,
    ) -> None:
        super().__init__(options=options)
        self.season_year = season_year
        resolved_dependencies = dependencies
        if resolved_dependencies is None:
            resolved_dependencies = (
                composition_factory or SeasonScraperCompositionFactory()
            ).build(options=self._options)

        self._season_year_resolver = resolved_dependencies.season_year_resolver
        self._season_pipeline = resolved_dependencies.season_pipeline
        self._domain_record_service = resolved_dependencies.domain_record_service
        self._table_parser = None
        self._refresh_pipeline_state()

    def extract_by_url(
        self,
        url: str,
        *,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        self.url = url
        self._refresh_pipeline_state(explicit_year=season_year)
        return super().fetch()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        _ = soup
        return InfoboxPayloadDTO([])

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        self._refresh_pipeline_state()
        sections = self._season_pipeline.collect(soup=soup, adapter=self)
        return SectionsPayloadDTO(SeasonPayloadDTO(sections=sections))

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        _ = soup
        _ = infobox_payload
        _ = tables_payload
        payload = self._domain_record_service.build_payload(sections_payload.data)
        return self._domain_record_service.assemble_record(
            SeasonDomainRecordInput(payload=payload),
        )

    def _refresh_pipeline_state(self, *, explicit_year: int | None = None) -> None:
        self.season_year = self._season_year_resolver.resolve(
            url=self.url,
            explicit_year=explicit_year,
            current_year=self.season_year,
        )
        self._season_pipeline.configure(url=self.url, season_year=self.season_year)
        self._table_parser = self._season_pipeline.table_parser
