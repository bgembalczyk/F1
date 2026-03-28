import warnings
from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.payloads import InfoboxPayload
from scrapers.base.payloads import SectionsPayload
from scrapers.base.payloads import TablesPayload
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.seasons.pipeline import SeasonParserSetBuilder
from scrapers.seasons.pipeline import SeasonSectionPipeline
from scrapers.seasons.pipeline import SeasonYearResolver
from scrapers.seasons.postprocess.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess.assembler import SeasonRecordSections
from scrapers.seasons.postprocess.contract import SeasonSectionContractPostProcessor
from scrapers.seasons.postprocess.payloads import SeasonSectionsPayload
from scrapers.seasons.sections.service import SeasonTextSectionExtractionService


class SingleSeasonScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        season_year: int | None = None,
        text_sections_service_factory: (
            Callable[[SectionAdapter], SeasonTextSectionExtractionService] | None
        ) = None,
        assembler: SeasonRecordAssembler | None = None,
        season_year_resolver: SeasonYearResolver | None = None,
        parser_set_builder: SeasonParserSetBuilder | None = None,
        season_pipeline: SeasonSectionPipeline | None = None,
    ) -> None:
        super().__init__(options=options)
        self.season_year = season_year
        self._season_year_resolver = season_year_resolver or SeasonYearResolver()
        resolved_parser_set_builder = parser_set_builder or SeasonParserSetBuilder(
            options=self._options,
            include_urls=self.include_urls,
        )
        self._season_pipeline = season_pipeline or SeasonSectionPipeline(
            parser_set_builder=resolved_parser_set_builder,
            text_sections_service_factory=text_sections_service_factory,
        )
        self._assembler = assembler or SeasonRecordAssembler()
        self._table_parser = None
        self._refresh_pipeline_state()

    def fetch_by_url(
        self,
        url: str,
        *,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        self.url = url
        self._refresh_pipeline_state(explicit_year=season_year)
        return super().fetch()

    def _build_post_processor(self) -> SeasonSectionContractPostProcessor:
        return SeasonSectionContractPostProcessor()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayload:
        _ = soup
        return InfoboxPayload(data=[])

    def _build_sections_payload(self, soup: BeautifulSoup) -> SeasonSectionsPayload:
        self._refresh_pipeline_state()
        return SeasonSectionsPayload(
            sections=self._season_pipeline.collect(soup=soup, adapter=self),
        )

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayload,
        sections_payload: SeasonSectionsPayload,
        tables_payload: TablesPayload,
    ) -> dict[str, Any]:
        _ = soup
        _ = infobox_payload
        _ = tables_payload
        sections = sections_payload.sections
        if not isinstance(sections, SeasonRecordSections):
            sections = SeasonRecordSections.empty()
        return self._assembler.assemble(sections)

    @staticmethod
    def _extract_year_from_url(url: str) -> int | None:
        warnings.warn(
            "SingleSeasonScraper._extract_year_from_url() is deprecated; use "
            "SeasonYearResolver.extract_from_url() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return SeasonYearResolver.extract_from_url(url)

    def _refresh_pipeline_state(self, *, explicit_year: int | None = None) -> None:
        self.season_year = self._season_year_resolver.resolve(
            url=self.url,
            explicit_year=explicit_year,
            current_year=self.season_year,
        )
        self._season_pipeline.configure(url=self.url, season_year=self.season_year)
        self._table_parser = self._season_pipeline.table_parser
