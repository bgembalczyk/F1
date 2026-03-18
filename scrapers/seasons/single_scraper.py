from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup

from models.domain_utils.season_urls import extract_season_year_from_url
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.seasons.pipeline import SeasonParserSetBuilder
from scrapers.seasons.pipeline import SeasonSectionPipeline
from scrapers.seasons.pipeline import SeasonYearResolver
from scrapers.seasons.postprocess.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess.assembler import SeasonRecordSections
from scrapers.seasons.postprocess.contract import SeasonSectionContractPostProcessor
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
    ) -> None:
        super().__init__(options=options)
        self.season_year = season_year
        self._season_year_resolver = SeasonYearResolver()
        self._season_pipeline = SeasonSectionPipeline(
            parser_set_builder=SeasonParserSetBuilder(
                options=self._options,
                include_urls=self.include_urls,
            ),
            text_sections_service_factory=text_sections_service_factory,
        )
        self._assembler = assembler or SeasonRecordAssembler()
        self._table_parser = None
        self._configure_pipeline()

    def fetch_by_url(
        self,
        url: str,
        *,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        self.url = url
        self.season_year = self._season_year_resolver.resolve(
            url=url,
            explicit_year=season_year,
            current_year=self.season_year,
        )
        self._configure_pipeline()
        return super().fetch()

    def _build_post_processor(self) -> SeasonSectionContractPostProcessor:
        return SeasonSectionContractPostProcessor()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        _ = soup
        return []

    def _build_sections_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        self._configure_pipeline()
        return [
            {
                "sections": self._season_pipeline.collect(soup=soup, adapter=self),
            },
        ]

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: list[dict[str, Any]],
        sections_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        _ = soup
        _ = infobox_payload
        payload = sections_payload[0] if sections_payload else {}
        sections = payload.get("sections")
        if not isinstance(sections, SeasonRecordSections):
            sections = SeasonRecordSections(
                entries=[],
                free_practice_drivers=[],
                calendar=[],
                cancelled_rounds=[],
                testing_venues_and_dates=[],
                results=[],
                non_championship_races=[],
                scoring_system=[],
                drivers_standings=[],
                constructors_standings=[],
                jim_clark_trophy=[],
                colin_chapman_trophy=[],
                south_african_formula_one_championship=[],
                british_formula_one_championship=[],
                regulation_changes=[],
                mid_season_changes=[],
            )
        return self._assembler.assemble(sections)

    @staticmethod
    def _extract_year_from_url(url: str) -> int | None:
        return extract_season_year_from_url(url)

    def _configure_pipeline(self) -> None:
        self.season_year = self._season_year_resolver.resolve(
            url=self.url,
            current_year=self.season_year,
        )
        self._season_pipeline.configure(
            url=self.url,
            season_year=self.season_year,
        )
        self._table_parser = self._season_pipeline.table_parser
